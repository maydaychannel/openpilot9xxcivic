import numpy as np
from collections import defaultdict

from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.common.numpy_fast import interp
from opendbc.can.can_define import CANDefine
from opendbc.can.parser import CANParser
from openpilot.selfdrive.car.honda.hondacan import CanBus, get_cruise_speed_conversion
from openpilot.selfdrive.car.honda.values import CAR, DBC, CarControllerParams
from openpilot.selfdrive.car.interfaces import CarStateBase

TransmissionType = car.CarParams.TransmissionType


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.frame = 0
    self.CCP = CarControllerParams(CP)

  def update(self, cp, cp_cam, cp_body):
    ret = car.CarState.new_message()
    ret.standstill = ret.vEgoRaw == 0
    ret.steerFaultPermanent = False
    # NO_TORQUE_ALERT_2 can be caused by bump or steering nudge from driver
    ret.steerFaultTemporary = False
    self.is_metric = not cp.vl["CAR_SPEED"]["IMPERIAL_UNIT"]
    ret.wheelSpeeds = self.get_wheel_speeds(
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FR"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RR"],
    )

    ret.vEgoRaw = float(np.mean([ret.wheelSpeeds.fl, ret.wheelSpeeds.fr, ret.wheelSpeeds.rl, ret.wheelSpeeds.rr]))
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.vEgoCluster = float(np.mean([ret.wheelSpeeds.fl, ret.wheelSpeeds.fr, ret.wheelSpeeds.rl, ret.wheelSpeeds.rr]))

    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_stalk(
      250, cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"], cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"])
    ret.brakeHoldActive = cp.vl["VSA_STATUS"]["BRAKE_HOLD_ACTIVE"] == 1

    gear = int(cp.vl[self.gearbox_msg]["GEAR_SHIFTER"])
    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(gear, None))

    ret.gas = cp.vl["POWERTRAIN_DATA"]["PEDAL_GAS"]
    ret.gasPressed = ret.gas > 1e-5

    ret.brake = cp.vl["VSA_STATUS"]["USER_BRAKE"]
    ret.cruiseState.enabled = cp.vl["POWERTRAIN_DATA"]["ACC_STATUS"] != 0
    ret.cruiseState.available = bool(cp.vl[self.main_on_sig_msg]["MAIN_ON"])
    return ret

  def get_can_parser(self, CP):
    messages = [
      ("ENGINE_DATA", 100),
      ("WHEEL_SPEEDS", 50),
      ("POWERTRAIN_DATA", 100),
      ("CAR_SPEED", 10),
      ("VSA_STATUS", 50),
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CanBus(CP).pt)

  @staticmethod
  def get_cam_can_parser(CP):
    messages = []

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CanBus(CP).camera)

