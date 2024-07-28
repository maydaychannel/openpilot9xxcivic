#!/usr/bin/env python3
from cereal import car
from panda import Panda
from openpilot.common.conversions import Conversions as CV
from openpilot.common.numpy_fast import interp
from openpilot.selfdrive.car.honda.values import CAR
from openpilot.selfdrive.car import create_button_events, get_safety_config
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "honda"
    ret.radarUnavailable = True
    ret.lateralParams.torqueBP, ret.lateralParams.torqueV = [[0, 4096], [0, 4096]]  # TODO: determine if there is a dead zone at the top end
    ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]]
    ret.wheelSpeedFactor = 1.025

    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 0.8

    return ret
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam, self.cp_body)

    events = self.create_common_events(ret, pcm_enable=False)

    ret.events = events.to_msg()

    return ret
