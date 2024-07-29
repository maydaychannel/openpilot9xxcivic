from dataclasses import dataclass, field
from enum import Enum, IntFlag

from cereal import car
from openpilot.common.conversions import Conversions as CV
from panda.python import uds
from openpilot.selfdrive.car import dbc_dict, CarSpecs, PlatformConfig, Platforms, DbcDict
from openpilot.selfdrive.car.docs_definitions import CarFootnote, CarHarness, CarDocs, CarParts, Column
from openpilot.selfdrive.car.fw_query_definitions import FwQueryConfig, Request, StdQueries, p16

Ecu = car.CarParams.Ecu
VisualAlert = car.CarControl.HUDControl.VisualAlert


class CarControllerParams:
  STEER_STEP = 1
  HUD_1_STEP = 50
  HUD_2_STEP = 25

  STEER_MAX = 300
  STEER_DRIVER_ALLOWANCE = 80
  STEER_DRIVER_MULTIPLIER = 3  # weight driver torque heavily
  STEER_DRIVER_FACTOR = 1  # from dbc
  STEER_DELTA_UP = 4
  STEER_DELTA_DOWN = 4

  def __init__(self, CP):
    pass


@dataclass
class HondaCarDocs(CarDocs):
  package: str = "Honda Sensing"
class HondaPlatformConfig(PlatformConfig):
  dbc_dict: DbcDict = field(default_factory=lambda: dbc_dict('07civic', 'ocelot_controls')),
class CAR(Platforms):
  config: HondaPlatformConfig
  CIVIC_07 = HondaPlatformConfig(
    [HondaCarDocs("Honda Civic", "All", min_steer_speed=3. * CV.MPH_TO_MS)],
    CarSpecs(mass=1379 * CV.LB_TO_KG, wheelbase=2.7, steerRatio=15.38, centerToFrontRatio=0.4, tireStiffnessFactor=0.8467),
    dbc_dict('07civic', 'ocelot_controls'),
  )

  HONDA_E = HondaPlatformConfig(
    [
      HondaCarDocs("Honda Civic", "All", min_steer_speed=3. * CV.MPH_TO_MS),
    ],
    # steerRatio: 11.82 is spec end-to-end
    CarSpecs(mass=1379 * CV.LB_TO_KG, wheelbase=2.7, steerRatio=15.38, centerToFrontRatio=0.4, tireStiffnessFactor=0.8467),
    dbc_dict(None, None),
  )

FW_QUERY_CONFIG = FwQueryConfig(
  requests=[
    # Currently used to fingerprint
    Request(
      [StdQueries.UDS_VERSION_REQUEST],
      [StdQueries.UDS_VERSION_RESPONSE],
      bus=1,
    ),
  ],
)


DBC = CAR.create_dbc_map()
