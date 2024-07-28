#!/usr/bin/env python3
from typing import NamedTuple
from openpilot.selfdrive.car.honda.values import CAR as HONDA

# TODO: add routes for these cars
non_tested_cars = [
  FORD.FORD_F_150_MK14,
  GM.CADILLAC_ATS,
  GM.HOLDEN_ASTRA,
  GM.CHEVROLET_MALIBU,
  HYUNDAI.GENESIS_G90,
  VOLKSWAGEN.VOLKSWAGEN_CRAFTER_MK2,  # need a route from an ACC-equipped Crafter
  SUBARU.SUBARU_FORESTER_HYBRID,
]


class CarTestRoute(NamedTuple):
  route: str
  car_model: Platform | None
  segment: int | None = None


routes = [
  CarTestRoute("a74b011b32b51b56|2020-07-26--17-09-36", HONDA.CIVIC_07),

]
