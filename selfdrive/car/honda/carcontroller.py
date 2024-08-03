from collections import namedtuple
from openpilot.common.conversions import Conversions as CV
from cereal import car
from openpilot.common.numpy_fast import clip, interp
from openpilot.common.realtime import DT_CTRL
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car import apply_toyota_steer_torque_limits
from openpilot.selfdrive.car.honda.hondacan import create_steer_command, create_new_steer_command
from openpilot.selfdrive.car.honda.values import Ecu, CarControllerParams, SteerLimitParams
from openpilot.selfdrive.car.interfaces import CarControllerBase

#stepperservo
def calc_steering_torque_hold(angle, vEgo):
  hold_BP = [-40.0, -6.0, -4.0, -3.0, -2.0, -1.0, -0.5,  0.5,  1.0,  2.0,  3.0,  4.0,  6.0, 40.0]
  hold_V  = [-12.0, -5.7, -5.0, -4.5, -4.0, -3.3, -2.5,  2.5,  3.3,  4.0,  4.5,  5.0,  5.7, 12.0]
  return interp(angle, hold_BP, hold_V) #todo substract angle offset

SAMPLING_FREQ = 100 #Hz
# Steer angle limits
ANGLE_MAX_BP = [5., 15., 30]  #m/s
ANGLE_MAX = [200., 20., 10.] #deg
ANGLE_RATE_BP = [0., 5., 15.]
ANGLE_RATE_WINDUP = [500., 80., 15.]     #deg/s windup rate limit
ANGLE_RATE_UNWIND = [500., 350., 40.]  #deg/s unwind rate limit
#end stepper
    
class CarController(CarControllerBase):
  def __init__(self, dbc_name, CP, VM):
   # self.CP = CP
   # self.CCP = CarControllerParams(CP)
    self.packer = CANPacker(dbc_name)
    self.last_steer = 0
   # self.frame = 0
    # StepperServo variables, redundant safety check with the board
    self.last_steer_tq = 0
    self.last_controls_enabled = False
    self.last_target_angle_lim = 0
    self.angle_control = False
    self.steer_angle_enabled = False
    self.last_fault_frame = -200
    self.planner_cnt = 0
    self.inertia_tq = 0.
    self.target_angle_delta = 0
    self.steer_tq_r = 0
    self.fake_ecus = set()
    self.fake_ecus.add(Ecu.fwdCamera)

  def update(self, enabled, CC, CS, now_nanos):
    # Send CAN commands
    can_sends = []
    #stepperservo
    new_steer = int(round(actuators.steer * CarControllerParams.STEER_MAX))
    apply_steer = apply_toyota_steer_torque_limits(new_steer, self.last_steer, 0, CarControllerParams)
    
    # steer angle
    angle_lim = interp(CS.out.vEgo, ANGLE_MAX_BP, ANGLE_MAX)
    target_angle_lim = clip(actuators.steeringAngleDeg, -angle_lim, angle_lim)
    if enabled:
      # windup slower
      if (self.last_target_angle_lim * target_angle_lim) > 0. and abs(target_angle_lim) > abs(self.last_target_angle_lim): #todo revise last_angle
        angle_rate_max = interp(CS.out.vEgo, ANGLE_RATE_BP, ANGLE_RATE_WINDUP) 
      else:
        angle_rate_max = interp(CS.out.vEgo, ANGLE_RATE_BP, ANGLE_RATE_UNWIND)
      
      # steer angle - don't allow too large delta
      MAX_SEC_BEHIND = 1 #seconds behind target. Target deltas behind more than 1s will be rejected by bmw_safety #todo implement real (speed) rate limiter?? check with panda. Replace MAX_SEC_BEHIND with a Hz?
      target_angle_lim = clip(target_angle_lim, self.last_target_angle_lim - angle_rate_max*MAX_SEC_BEHIND, self.last_target_angle_lim + angle_rate_max*MAX_SEC_BEHIND)
      
      self.target_angle_delta =  target_angle_lim - CS.out.steeringAngleDeg
      angle_step_max = angle_rate_max / SAMPLING_FREQ  #max angle step per single sample
      angle_step = clip(self.target_angle_delta, -angle_step_max, angle_step_max) #apply angle step
      self.steer_rate_limited = self.target_angle_delta != angle_step #advertise steer beeing rate limited
      # steer torque
      I_steering = 0 #estimated moment of inertia
      
      PLANNER_SAMPLING_SUBRATE = 6 #planner updates target angle every 4 or 6 samples
      if target_angle_lim != self.last_target_angle_lim or self.planner_cnt >= PLANNER_SAMPLING_SUBRATE-1:
        steer_acc = (target_angle_lim - self.last_target_angle_lim) * SAMPLING_FREQ  #desired acceleration
        remaining_steer_torque = self.inertia_tq * (PLANNER_SAMPLING_SUBRATE - self.planner_cnt -1) #remaining torque to be applied if target_angle_lim was updated earlier than PLANNER_SAMPLING_SUBRATE
        self.inertia_tq = I_steering * steer_acc / PLANNER_SAMPLING_SUBRATE * CV.DEG_TO_RAD  #kg*m^2 * rad/s^2 = N*m (torque)
        self.inertia_tq += remaining_steer_torque / PLANNER_SAMPLING_SUBRATE
        self.planner_cnt = 0
      else:
        self.planner_cnt += 1
      
      # add feed-forward and inertia compensation
      feedforward = calc_steering_torque_hold(target_angle_lim, CS.out.vEgo)
      steer_tq = feedforward + actuators.steer + self.inertia_tq
      # explicitly clip torque before sending on CAN
      steer_tq = clip(steer_tq, -SteerLimitParams.MAX_STEERING_TQ, SteerLimitParams.MAX_STEERING_TQ)
      self.steer_tq_r = steer_tq * (-1)    # Switch StepperServo rotation
    elif not enabled and self.last_controls_enabled: #falling edge - send cancel CAN message
      self.target_angle_delta = 0
      steer_tq = 0
      self.steer_tq_r = 0
      can_sends.append(create_new_steer_command(self.packer, apply_steer_req, self.target_angle_delta, self.steer_tq_r, frame)) 
      self.last_steer_tq = steer_tq
      self.last_target_angle_lim = target_angle_lim
      self.last_controls_enabled = enabled
    if Ecu.fwdCamera in self.fake_ecus:
      # Original steer_command
      can_sends.append(create_steer_command(self.packer, apply_steer, apply_steer_req, frame))
      # # StepperServoCan steer_command
      can_sends.append(create_new_steer_command(self.packer, apply_steer_req, self.target_angle_delta, self.steer_tq_r, frame))
    
    return new_actuators, can_sends
