from dataclasses import dataclass, field
from enum import Enum, IntFlag

from cereal import car
from openpilot.common.conversions import Conversions as CV
from panda.python import uds
from openpilot.selfdrive.car import dbc_dict, CarSpecs, PlatformConfig, Platforms, dbc_dict
from openpilot.selfdrive.car.docs_definitions import CarFootnote, CarHarness, CarDocs, CarParts, Column
from openpilot.selfdrive.car.fw_query_definitions import FwQueryConfig, Request, StdQueries, p16

Ecu = car.CarParams.Ecu
VisualAlert = car.CarControl.HUDControl.VisualAlert


class CarControllerParams:
  # Allow small margin below -3.5 m/s^2 from ISO 15622:2018 since we
  # perform the closed loop control, and might need some
  # to apply some more braking if we're on a downhill slope.
  # Our controller should still keep the 2 second average above
  # -3.5 m/s^2 as per planner limits
  NIDEC_ACCEL_MIN = -4.0  # m/s^2
  NIDEC_ACCEL_MAX = 1.6  # m/s^2, lower than 2.0 m/s^2 for tuning reasons

  NIDEC_ACCEL_LOOKUP_BP = [-1., 0., .6]
  NIDEC_ACCEL_LOOKUP_V = [-4.8, 0., 2.0]

  NIDEC_MAX_ACCEL_V = [0.5, 2.4, 1.4, 0.6]
  NIDEC_MAX_ACCEL_BP = [0.0, 4.0, 10., 20.]

  NIDEC_GAS_MAX = 198  # 0xc6
  NIDEC_BRAKE_MAX = 1024 // 4
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
    [
      HondaCarDocs("Honda Civic", "All", min_steer_speed=3. * CV.MPH_TO_MS),
    ],
    # steerRatio: 11.82 is spec end-to-end
    CarSpecs(mass=1379 * CV.LB_TO_KG, wheelbase=2.7, steerRatio=15.38, centerToFrontRatio=0.4, tireStiffnessFactor=0.8467),
    dbc_dict('07civic', 'ocelot_controls'),
  )

  HONDA_E = HondaPlatformConfig(
    [
      HondaCarDocs("Honda Civic", "All", min_steer_speed=3. * CV.MPH_TO_MS),
    ],
    # steerRatio: 11.82 is spec end-to-end
    CarSpecs(mass=1379 * CV.LB_TO_KG, wheelbase=2.7, steerRatio=15.38, centerToFrontRatio=0.4, tireStiffnessFactor=0.8467),
    dbc_dict('07civic', 'ocelot_controls'),
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
