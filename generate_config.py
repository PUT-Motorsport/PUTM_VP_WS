#!/usr/bin/env python3

from pathlib import Path
import kconfiglib

ROOT = Path(__file__).resolve().parent

KCONFIG_PATH = ROOT / "Kconfig"
CONFIG_PATH = ROOT / ".config"
OUTPUT_PATH = ROOT / "config" / "vehicle.yaml"

if not CONFIG_PATH.is_file():
    raise FileNotFoundError(f"Configuration not found: {CONFIG_PATH}")

kconf = kconfiglib.Kconfig(str(KCONFIG_PATH))
kconf.load_config(str(CONFIG_PATH))


def get_int(name):
    symbol = kconf.syms.get(name)

    if symbol is None:
        raise KeyError(f"Missing Kconfig symbol: {name}")

    return int(symbol.str_value)


def get_bool(name):
    symbol = kconf.syms.get(name)

    if symbol is None:
        raise KeyError(f"Missing Kconfig symbol: {name}")

    return symbol.str_value == "y"


enable_mpc = get_bool("ENABLE_MPC")

max_moment = get_int("MAX_MOMENT")
min_torque = get_int("MIN_TORQUE")

enable_tc = get_bool("ENABLE_TC")
tc_slip_ratio_limit = get_int("TC_SLIP_RATIO_LIMIT") / 1000.0
tc_torque_reduction_gain = get_int("TC_TORQUE_REDUCTION_GAIN")

ku_denominator = get_int("KU_DENOMINATOR")

if ku_denominator <= 0:
    raise ValueError("KU_DENOMINATOR must be greater than 0")

ku = 1.0 / ku_denominator

regen_braking_factor = get_int("REGEN_BRAKING_FACTOR") / 100.0


if min_torque > max_moment:
    raise ValueError("MIN_TORQUE cannot exceed MAX_MOMENT")

if tc_slip_ratio_limit < 1.0:
    raise ValueError("TC_SLIP_RATIO_LIMIT must be >= 1.0")

if not 0.0 <= regen_braking_factor <= 1.0:
    raise ValueError("REGEN_BRAKING_FACTOR must be between 0 and 1")


yaml_content = f"""\
/controller:
  ros__parameters:

    # Control Mode
    enable_mpc: {str(enable_mpc).lower()}

    # Torque Configuration
    max_moment: {float(max_moment)}
    min_torque: {float(min_torque)}

    # Traction Control
    enable_tc: {str(enable_tc).lower()}
    tc_slip_ratio_limit: {tc_slip_ratio_limit}
    tc_torque_reduction_gain: {float(tc_torque_reduction_gain)}

    # Vehicle Dynamics
    ku: {ku}

    # Regenerative Braking
    regen_braking_factor: {regen_braking_factor}
"""

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text() != yaml_content:
    OUTPUT_PATH.write_text(yaml_content)

print(f"Generated: {OUTPUT_PATH}")
print()
print("PUTM Controller configuration:")
print(f"  MPC enabled:          {enable_mpc}")
print(f"  Max moment:           {max_moment} Nm")
print(f"  Min torque:           {min_torque} Nm")
print(f"  Traction control:     {enable_tc}")
print(f"  TC slip ratio limit:  {tc_slip_ratio_limit}")
print(f"  TC reduction gain:    {tc_torque_reduction_gain}")
print(f"  Ku:                   {ku}")
print(f"  Regen braking factor: {regen_braking_factor}")