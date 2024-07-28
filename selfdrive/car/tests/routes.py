#!/usr/bin/env python3
from typing import NamedTuple

from openpilot.selfdrive.car.chrysler.values import CAR as CHRYSLER
from openpilot.selfdrive.car.gm.values import CAR as GM
from openpilot.selfdrive.car.ford.values import CAR as FORD
from openpilot.selfdrive.car.honda.values import CAR as HONDA
from openpilot.selfdrive.car.hyundai.values import CAR as HYUNDAI
from openpilot.selfdrive.car.nissan.values import CAR as NISSAN
from openpilot.selfdrive.car.mazda.values import CAR as MAZDA
from openpilot.selfdrive.car.subaru.values import CAR as SUBARU
from openpilot.selfdrive.car.toyota.values import CAR as TOYOTA
from openpilot.selfdrive.car.values import Platform
from openpilot.selfdrive.car.volkswagen.values import CAR as VOLKSWAGEN
from openpilot.selfdrive.car.tesla.values import CAR as TESLA
from openpilot.selfdrive.car.body.values import CAR as COMMA

# TODO: add routes for these cars
non_tested_cars = [
  FORD.FORD_F_150_MK14,
  GM.CADILLAC_ATS,
  GM.HOLDEN_ASTRA,
  GM.CHEVROLET_MALIBU,
  HYUNDAI.GENESIS_G90,
  HONDA.HONDA_ODYSSEY_CHN,
  VOLKSWAGEN.VOLKSWAGEN_CRAFTER_MK2,  # need a route from an ACC-equipped Crafter
  SUBARU.SUBARU_FORESTER_HYBRID,
]


class CarTestRoute(NamedTuple):
  route: str
  car_model: Platform | None
  segment: int | None = None


routes = [
  CarTestRoute("efdf9af95e71cd84|2022-05-13--19-03-31", COMMA.COMMA_BODY),

  CarTestRoute("0c94aa1e1296d7c6|2021-05-05--19-48-37", CHRYSLER.JEEP_GRAND_CHEROKEE),
  CarTestRoute("91dfedae61d7bd75|2021-05-22--20-07-52", CHRYSLER.JEEP_GRAND_CHEROKEE_2019),
  CarTestRoute("420a8e183f1aed48|2020-03-05--07-15-29", CHRYSLER.CHRYSLER_PACIFICA_2018_HYBRID),  # 2017
  CarTestRoute("43a685a66291579b|2021-05-27--19-47-29", CHRYSLER.CHRYSLER_PACIFICA_2018),
  CarTestRoute("378472f830ee7395|2021-05-28--07-38-43", CHRYSLER.CHRYSLER_PACIFICA_2018_HYBRID),
  CarTestRoute("8190c7275a24557b|2020-01-29--08-33-58", CHRYSLER.CHRYSLER_PACIFICA_2019_HYBRID),
  CarTestRoute("3d84727705fecd04|2021-05-25--08-38-56", CHRYSLER.CHRYSLER_PACIFICA_2020),
  CarTestRoute("221c253375af4ee9|2022-06-15--18-38-24", CHRYSLER.RAM_1500_5TH_GEN),
  CarTestRoute("8fb5eabf914632ae|2022-08-04--17-28-53", CHRYSLER.RAM_HD_5TH_GEN, segment=6),
  CarTestRoute("3379c85aeedc8285|2023-12-07--17-49-39", CHRYSLER.DODGE_DURANGO),

  CarTestRoute("54827bf84c38b14f|2023-01-25--14-14-11", FORD.FORD_BRONCO_SPORT_MK1),
  CarTestRoute("f8eaaccd2a90aef8|2023-05-04--15-10-09", FORD.FORD_ESCAPE_MK4),
  CarTestRoute("62241b0c7fea4589|2022-09-01--15-32-49", FORD.FORD_EXPLORER_MK6),
  CarTestRoute("e886087f430e7fe7|2023-06-16--23-06-36", FORD.FORD_FOCUS_MK4),
  CarTestRoute("bd37e43731e5964b|2023-04-30--10-42-26", FORD.FORD_MAVERICK_MK1),
  CarTestRoute("112e4d6e0cad05e1|2023-11-14--08-21-43", FORD.FORD_F_150_LIGHTNING_MK1),
  CarTestRoute("83a4e056c7072678|2023-11-13--16-51-33", FORD.FORD_MUSTANG_MACH_E_MK1),
  CarTestRoute("37998aa0fade36ab/00000000--48f927c4f5", FORD.FORD_RANGER_MK2),
  #TestRoute("f1b4c567731f4a1b|2018-04-30--10-15-35", FORD.FUSION),

  CarTestRoute("7cc2a8365b4dd8a9|2018-12-02--12-10-44", GM.GMC_ACADIA),
  CarTestRoute("aa20e335f61ba898|2019-02-05--16-59-04", GM.BUICK_REGAL),
  CarTestRoute("75a6bcb9b8b40373|2023-03-11--22-47-33", GM.BUICK_LACROSSE),
  CarTestRoute("e746f59bc96fd789|2024-01-31--22-25-58", GM.CHEVROLET_EQUINOX),
  CarTestRoute("ef8f2185104d862e|2023-02-09--18-37-13", GM.CADILLAC_ESCALADE),
  CarTestRoute("46460f0da08e621e|2021-10-26--07-21-46", GM.CADILLAC_ESCALADE_ESV),
  CarTestRoute("168f8b3be57f66ae|2023-09-12--21-44-42", GM.CADILLAC_ESCALADE_ESV_2019),
  CarTestRoute("c950e28c26b5b168|2018-05-30--22-03-41", GM.CHEVROLET_VOLT),
  CarTestRoute("f08912a233c1584f|2022-08-11--18-02-41", GM.CHEVROLET_BOLT_EUV, segment=1),
  CarTestRoute("555d4087cf86aa91|2022-12-02--12-15-07", GM.CHEVROLET_BOLT_EUV, segment=14),  # Bolt EV
  CarTestRoute("38aa7da107d5d252|2022-08-15--16-01-12", GM.CHEVROLET_SILVERADO),
  CarTestRoute("5085c761395d1fe6|2023-04-07--18-20-06", GM.CHEVROLET_TRAILBLAZER),

  CarTestRoute("0e7a2ba168465df5|2020-10-18--14-14-22", HONDA.ACURA_RDX_3G),
  CarTestRoute("a74b011b32b51b56|2020-07-26--17-09-36", HONDA.HONDA_CIVIC),

  # Segments that test specific issues
  # Controls mismatch due to standstill threshold
  CarTestRoute("bec2dcfde6a64235|2022-04-08--14-21-32", HONDA.HONDA_CRV_HYBRID, segment=22),
]
