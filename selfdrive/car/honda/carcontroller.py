from collections import namedtuple

from cereal import car
from openpilot.common.numpy_fast import clip, interp
from openpilot.common.realtime import DT_CTRL
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car.honda import hondacan
from openpilot.selfdrive.car.honda.values import CarControllerParams
from openpilot.selfdrive.car.interfaces import CarControllerBase

class CarController(CarControllerBase):
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    self.CCP = CarControllerParams(CP)
    self.packer_pt = CANPacker(dbc_name)
    self.apply_steer_last = 0
    self.frame = 0

  def update(self, CC, CS, now_nanos):
    actuators = CC.actuators
    # Send CAN commands
    can_sends = []
    apply_steer = 0
    self.apply_steer_last = apply_steer
    new_actuators = actuators.as_builder()
    new_actuators.steer = self.apply_steer_last / self.CCP.STEER_MAX
    new_actuators.steerOutputCan = self.apply_steer_last

    self.frame += 1
    return new_actuators, can_sends
