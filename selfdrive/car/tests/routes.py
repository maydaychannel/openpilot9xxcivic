#!/usr/bin/env python3
from typing import NamedTuple
from openpilot.selfdrive.car.honda.values import CAR as HONDA


class CarTestRoute(NamedTuple):
  route: str
  car_model: Platform | None
  segment: int | None = None


routes = [
  CarTestRoute("a74b011b32b51b56|2020-07-26--17-09-36", HONDA.CIVIC_07),

]
