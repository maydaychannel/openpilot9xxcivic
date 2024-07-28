from collections import namedtuple

from cereal import car
from openpilot.common.numpy_fast import clip, interp
from openpilot.common.realtime import DT_CTRL
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car.honda import hondacan
from openpilot.selfdrive.car.honda.values import CarControllerParams
from openpilot.selfdrive.car.interfaces import CarControllerBase
from openpilot.selfdrive.controls.lib.drive_helpers import rate_limit

VisualAlert = car.CarControl.HUDControl.VisualAlert
LongCtrlState = car.CarControl.Actuators.LongControlState

def process_hud_alert(hud_alert):
  # initialize to no alert
  fcw_display = 0
  steer_required = 0
  acc_alert = 0

  # priority is: FCW, steer required, all others
  if hud_alert == VisualAlert.fcw:
    fcw_display = VISUAL_HUD[hud_alert.raw]
  elif hud_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
    steer_required = VISUAL_HUD[hud_alert.raw]
  else:
    acc_alert = VISUAL_HUD[hud_alert.raw]

  return fcw_display, steer_required, acc_alert


HUDData = namedtuple("HUDData",
                     ["pcm_accel", "v_cruise", "lead_visible",
                      "lanes_visible", "fcw", "acc_alert", "steer_required", "lead_distance_bars"])


def rate_limit_steer(new_steer, last_steer):
  # TODO just hardcoded ramp to min/max in 0.33s for all Honda
  MAX_DELTA = 3 * DT_CTRL
  return clip(new_steer, last_steer - MAX_DELTA, last_steer + MAX_DELTA)


class CarController(CarControllerBase):
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    self.packer = CANPacker(dbc_name)
    self.params = CarControllerParams(CP)
    self.CAN = hondacan.CanBus(CP)
    self.frame = 0

    self.braking = False
    self.brake_steady = 0.
    self.brake_last = 0.
    self.apply_brake_last = 0
    self.last_pump_ts = 0.
    self.stopping_counter = 0

    self.accel = 0.0
    self.speed = 0.0
    self.gas = 0.0
    self.brake = 0.0
    self.last_steer = 0.0

  def update(self, CC, CS, now_nanos):
    actuators = CC.actuators
    hud_control = CC.hudControl
    conversion = hondacan.get_cruise_speed_conversion(self.CP.carFingerprint, CS.is_metric)
    hud_v_cruise = hud_control.setSpeed / conversion if hud_control.speedVisible else 255
    pcm_cancel_cmd = CC.cruiseControl.cancel

    if CC.longActive:
      accel = actuators.accel
      gas, brake = compute_gas_brake(actuators.accel, CS.out.vEgo, self.CP.carFingerprint)
    else:
      accel = 0.0
      gas, brake = 0.0, 0.0

    # *** rate limit steer ***
    limited_steer = rate_limit_steer(actuators.steer, self.last_steer)
    self.last_steer = limited_steer

    # steer torque is converted back to CAN reference (positive when steering right)
    apply_steer = int(interp(-limited_steer * self.params.STEER_MAX,
                             self.params.STEER_LOOKUP_BP, self.params.STEER_LOOKUP_V))

    # Send CAN commands
    can_sends = []
    # Send steering command.
    can_sends.append(hondacan.create_steering_control(self.packer, self.CAN, apply_steer, CC.latActive, self.CP.carFingerprint,
                                                      CS.CP.openpilotLongitudinalControl))
    can_sends.append(create_new_steer_command(self.packer, apply_steer_req, self.target_angle_delta, self.steer_tq_r, frame))

    new_actuators = actuators.as_builder()
    new_actuators.speed = self.speed
    new_actuators.accel = self.accel
    new_actuators.gas = self.gas
    new_actuators.brake = self.brake
    new_actuators.steer = self.last_steer
    new_actuators.steerOutputCan = apply_steer

    self.frame += 1
    return new_actuators, can_sends
