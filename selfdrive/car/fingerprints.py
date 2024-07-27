from openpilot.selfdrive.car.interfaces import get_interface_attr
from openpilot.selfdrive.car.body.values import CAR as BODY
from openpilot.selfdrive.car.chrysler.values import CAR as CHRYSLER
from openpilot.selfdrive.car.ford.values import CAR as FORD
from openpilot.selfdrive.car.gm.values import CAR as GM
from openpilot.selfdrive.car.honda.values import CAR as HONDA
from openpilot.selfdrive.car.hyundai.values import CAR as HYUNDAI
from openpilot.selfdrive.car.mazda.values import CAR as MAZDA
from openpilot.selfdrive.car.mock.values import CAR as MOCK
from openpilot.selfdrive.car.nissan.values import CAR as NISSAN
from openpilot.selfdrive.car.subaru.values import CAR as SUBARU
from openpilot.selfdrive.car.tesla.values import CAR as TESLA
from openpilot.selfdrive.car.toyota.values import CAR as TOYOTA
from openpilot.selfdrive.car.volkswagen.values import CAR as VW

FW_VERSIONS = get_interface_attr('FW_VERSIONS', combine_brands=True, ignore_none=True)
_FINGERPRINTS = get_interface_attr('FINGERPRINTS', combine_brands=True, ignore_none=True)

_DEBUG_ADDRESS = {1880: 8}   # reserved for debug purposes


def is_valid_for_fingerprint(msg, car_fingerprint: dict[int, int]):
  adr = msg.address
  # ignore addresses that are more than 11 bits
  return (adr in car_fingerprint and car_fingerprint[adr] == len(msg.dat)) or adr >= 0x800


def eliminate_incompatible_cars(msg, candidate_cars):
  """Removes cars that could not have sent msg.

     Inputs:
      msg: A cereal/log CanData message from the car.
      candidate_cars: A list of cars to consider.

     Returns:
      A list containing the subset of candidate_cars that could have sent msg.
  """
  compatible_cars = []

  for car_name in candidate_cars:
    car_fingerprints = _FINGERPRINTS[car_name]

    for fingerprint in car_fingerprints:
      # add alien debug address
      if is_valid_for_fingerprint(msg, fingerprint | _DEBUG_ADDRESS):
        compatible_cars.append(car_name)
        break

  return compatible_cars


def all_known_cars():
  """Returns a list of all known car strings."""
  return list({*FW_VERSIONS.keys(), *_FINGERPRINTS.keys()})


def all_legacy_fingerprint_cars():
  """Returns a list of all known car strings, FPv1 only."""
  return list(_FINGERPRINTS.keys())


# A dict that maps old platform strings to their latest representations
MIGRATION = {
  "HYUNDAI ELANTRA LIMITED ULTIMATE 2017": HYUNDAI.HYUNDAI_ELANTRA,
  "HYUNDAI SANTA FE LIMITED 2019": HYUNDAI.HYUNDAI_SANTA_FE,
  "HYUNDAI TUCSON DIESEL 2019": HYUNDAI.HYUNDAI_TUCSON,
  "KIA OPTIMA 2016": HYUNDAI.KIA_OPTIMA_G4,
  "KIA OPTIMA 2019": HYUNDAI.KIA_OPTIMA_G4_FL,
  "KIA OPTIMA SX 2019 & 2016": HYUNDAI.KIA_OPTIMA_G4_FL,
  "LEXUS CT 200H 2018": TOYOTA.LEXUS_CTH,
  "LEXUS ES 300H 2018": TOYOTA.LEXUS_ES,
  "LEXUS ES 300H 2019": TOYOTA.LEXUS_ES_TSS2,
  "LEXUS IS300 2018": TOYOTA.LEXUS_IS,
  "LEXUS NX300 2018": TOYOTA.LEXUS_NX,
  "LEXUS NX300H 2018": TOYOTA.LEXUS_NX,
  "LEXUS RX 350 2016": TOYOTA.LEXUS_RX,
  "LEXUS RX350 2020": TOYOTA.LEXUS_RX_TSS2,
  "LEXUS RX450 HYBRID 2020": TOYOTA.LEXUS_RX_TSS2,
  "TOYOTA SIENNA XLE 2018": TOYOTA.TOYOTA_SIENNA,
  "TOYOTA C-HR HYBRID 2018": TOYOTA.TOYOTA_CHR,
  "TOYOTA COROLLA HYBRID TSS2 2019": TOYOTA.TOYOTA_COROLLA_TSS2,
  "TOYOTA RAV4 HYBRID 2019": TOYOTA.TOYOTA_RAV4_TSS2,
  "LEXUS ES HYBRID 2019": TOYOTA.LEXUS_ES_TSS2,
  "LEXUS NX HYBRID 2018": TOYOTA.LEXUS_NX,
  "LEXUS NX HYBRID 2020": TOYOTA.LEXUS_NX_TSS2,
  "LEXUS RX HYBRID 2020": TOYOTA.LEXUS_RX_TSS2,
  "TOYOTA ALPHARD HYBRID 2021": TOYOTA.TOYOTA_ALPHARD_TSS2,
  "TOYOTA AVALON HYBRID 2019": TOYOTA.TOYOTA_AVALON_2019,
  "TOYOTA AVALON HYBRID 2022": TOYOTA.TOYOTA_AVALON_TSS2,
  "TOYOTA CAMRY HYBRID 2018": TOYOTA.TOYOTA_CAMRY,
  "TOYOTA CAMRY HYBRID 2021": TOYOTA.TOYOTA_CAMRY_TSS2,
  "TOYOTA C-HR HYBRID 2022": TOYOTA.TOYOTA_CHR_TSS2,
  "TOYOTA HIGHLANDER HYBRID 2020": TOYOTA.TOYOTA_HIGHLANDER_TSS2,
  "TOYOTA RAV4 HYBRID 2022": TOYOTA.TOYOTA_RAV4_TSS2_2022,
  "TOYOTA RAV4 HYBRID 2023": TOYOTA.TOYOTA_RAV4_TSS2_2023,
  "TOYOTA HIGHLANDER HYBRID 2018": TOYOTA.TOYOTA_HIGHLANDER,
  "LEXUS ES HYBRID 2018": TOYOTA.LEXUS_ES,
  "LEXUS RX HYBRID 2017": TOYOTA.LEXUS_RX,
  "HYUNDAI TUCSON HYBRID 4TH GEN": HYUNDAI.HYUNDAI_TUCSON_4TH_GEN,
  "KIA SPORTAGE HYBRID 5TH GEN": HYUNDAI.KIA_SPORTAGE_5TH_GEN,
  "KIA SORENTO PLUG-IN HYBRID 4TH GEN": HYUNDAI.KIA_SORENTO_HEV_4TH_GEN,
  "CADILLAC ESCALADE ESV PLATINUM 2019": GM.CADILLAC_ESCALADE_ESV_2019,

  # Removal of platform_str, see https://github.com/commaai/openpilot/pull/31868/
  "mock": MOCK.MOCK,
}
