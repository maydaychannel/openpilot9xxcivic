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

  #stepperservo stuff
  STEER_MAX = 1500
  STEER_DELTA_UP = 3       # 1.5s time to peak torque (original value 10)
  STEER_DELTA_DOWN = 25     # always lower than 45 otherwise the Rav4 faults (Prius seems ok with 50)
  STEER_ERROR_MAX = 350 
#stepperservo params
class SteerActuatorParams: # stepper parameters
  STEER_BACKLASH = 1 #deg
  def __init__(self, CP):
    pass
# Steer torque limits for StepperServo
class SteerLimitParams: #controls running @ 100hz
  MAX_STEERING_TQ = 12  # Nm
  STEER_DELTA_UP = 10 / 100       # 10Nm/s
  STEER_DELTA_DOWN = 1000 / 100     # 10Nm/sample - no limit
  STEER_ERROR_MAX = 999     # max delta between torque cmd and torque motor

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
      [StdQueries.MANUFACTURER_SOFTWARE_VERSION_REQUEST],
      [StdQueries.MANUFACTURER_SOFTWARE_VERSION_RESPONSE],
      bus=0,
    ),
  ],
)


DBC = CAR.create_dbc_map()
