#!/usr/bin/env python3
from typing import NamedTuple
from openpilot.selfdrive.car.honda.values import CAR as HONDA
from openpilot.selfdrive.car.values import Platform
from openpilot.selfdrive.car.ford.values import CAR as FORD
class CarTestRoute(NamedTuple):
  route: str
  car_model: Platform | None
  segment: int | None = None

non_tested_cars = [
  FORD.FORD_F_150_MK14,
]

routes = [
  CarTestRoute("a74b011b32b51b56|2020-07-26--17-09-36", HONDA.CIVIC_07),

]
