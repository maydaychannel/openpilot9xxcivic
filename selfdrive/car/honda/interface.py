from cereal import car
from openpilot.selfdrive.car import get_safety_config
from openpilot.selfdrive.car.honda.values import CAR, SteerLimitParams
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

# steer control i think

def detect_stepper_override(steerCmd, steerAct, vEgo, centering_ceoff, SteerFrictionTq):
  # when steering released (or lost steps), what angle will it return to
  # if we are above that angle, we can detect things
  releaseAngle = SteerFrictionTq / (max(vEgo, 1) ** 2 * centering_ceoff)

  override = False
  marginVal = 1
  if abs(steerCmd) > releaseAngle:  # for higher angles we steering will not move outward by itself with stepper on
    if steerCmd > 0:
      override |= steerAct - steerCmd > marginVal  # driver overrode from right to more right
      override |= steerAct < 0  # releaseAngle -3  # driver overrode from right to opposite direction
    else:
      override |= steerAct - steerCmd < -marginVal  # driver overrode from left to more left
      override |= steerAct > 0  # -releaseAngle +3 # driver overrode from left to opposite direction
  # else:
    # override |= abs(steerAct) > releaseAngle + marginVal  # driver overrode to an angle where steering will not go by itself
  return override

class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "honda"
    ret.radarUnavailable = True
    ret.lateralParams.torqueBP, ret.lateralParams.torqueV = [[0, 4096], [0, 4096]]  # TODO: determine if there is a dead zone at the top end
    ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]]
    ret.wheelSpeedFactor = 1.025
    
    ###added from killinen's stepperservo
    ret.steerControlType = car.CarParams.SteerControlType.angle
    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 0.8
    ret.lateralTuning.init('pid')
    ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[5.5, 30.], [5.5, 30.]]
    ret.lateralTuning.pid.kiV, ret.lateralTuning.pid.kpV = [[0.0, 0.0], [0.5, 3]]
    ret.lateralTuning.pid.kf = 0.00003
    ret.steerMaxBP = [0.]
    ret.steerMaxV = [SteerLimitParams.MAX_STEERING_TQ]
    ##end from killinen
    return ret
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam, self.cp_body)

    events = self.create_common_events(ret, pcm_enable=False)

    ret.events = events.to_msg()

    return ret
