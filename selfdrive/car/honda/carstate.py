import numpy as np
from collections import defaultdict

from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.common.numpy_fast import interp, mean
from opendbc.can.can_define import CANDefine
from opendbc.can.parser import CANParser
from openpilot.selfdrive.car.honda.hondacan import CanBus
from openpilot.selfdrive.car.honda.values import CAR, DBC, CarControllerParams
from openpilot.selfdrive.car.interfaces import CarStateBase

TransmissionType = car.CarParams.TransmissionType


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    #self.frame = 0
    #self.CCP = CarControllerParams(CP)

  def update(self, cp, cp_cam):
    ret = car.CarState.new_message()
    ret.standstill = ret.vEgoRaw == 0
    ret.steerFaultPermanent = False
    ret.steerFaultTemporary = False
    #ret.steeringTorqueEps = cp.vl["STEERING_STATUS"]['STEERING_TORQUE']
    self.is_metric = not cp.vl["CAR_SPEED"]["IMPERIAL_UNIT"]
    ret.wheelSpeeds = self.get_wheel_speeds(
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_FR"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RL"],
      cp.vl["WHEEL_SPEEDS"]["WHEEL_SPEED_RR"],
    )

    ret.vEgoRaw = float(np.mean([ret.wheelSpeeds.fl, ret.wheelSpeeds.fr, ret.wheelSpeeds.rl, ret.wheelSpeeds.rr]))
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.vEgoCluster = ret.vEgo

    return ret
  @staticmethod
  def get_can_parser(CP):
    messages = [
      ("ENGINE_DATA", 100),
      ("WHEEL_SPEEDS", 50),
      ("POWERTRAIN_DATA", 100),
      #("STEERING_STATUS", "STEERING_TORQUE", 100),
      ("CAR_SPEED", 10),
      ("VSA_STATUS", 50),
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, 0)

  #@staticmethod
  #def get_cam_can_parser(CP):
  #  messages = [
   #        ("STEERING_TORQUE", "STEERING_STATUS", 0),]
  #  return CANParser('ocelot_controls', messages, 1)

