from cereal import car
from openpilot.selfdrive.car.honda.values import CAR

Ecu = car.CarParams.Ecu

# Modified FW can be identified by the second dash being replaced by a comma
# For example: `b'39990-TVA,A150\x00\x00'`
#
# TODO: vsa is "essential" for fpv2 but doesn't appear on some CAR.FREED models

FINGERPRINTS = {
  CAR.CIVIC_07: [{
    57: 2, 310: 8, 314: 8, 319: 8, 344: 8, 356: 8, 380: 8, 398: 3, 420: 8, 432: 7, 464: 8, 476: 4, 660: 8, 773: 2, 777: 8, 800: 3, 804: 8, 892: 5, 1029: 8, 1036: 8, 1064: 7, 1108: 3, 1125: 7
  }]
}

FW_VERSIONS = {
  CAR.HONDA_E: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TYF-N030\x00\x00',
    ],
  },
}
