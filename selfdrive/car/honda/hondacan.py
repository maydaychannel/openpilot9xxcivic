from openpilot.comma.conversions import Conversions as CV
def create_new_steer_command(packer, mode, steer_delta, steer_tq, frame):
  """Creates a CAN message for the actuator STEERING_COMMAND"""
#  packer = CANPacker('ocelot_controls')
  values = {
    "SERVO_COUNTER": frame % 0xF,
    "STEER_MODE": mode,
    "STEER_ANGLE": steer_delta,
    "STEER_TORQUE": steer_tq,
  }
  msg = packer.make_can_msg("STEERING_COMMAND", 0, values)
  addr = msg[0]
  dat  = msg[2]

  values["SERVO_CHECKSUM"] = calc_checksum_8bit(dat, addr)
  return packer.make_can_msg("STEERING_COMMAND", 0, values) #bus 2 is the actuator CAN bus

def get_cruise_speed_conversion(car_fingerprint: str, is_metric: bool) -> float:
  return CV.KPH_TO_MS
