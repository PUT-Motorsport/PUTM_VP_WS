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

nominal_motor_torque_nm = 9.8
max_moment = get_int("MAX_MOMENT") * nominal_motor_torque_nm / 100.0
min_torque = get_int("MIN_TORQUE") * nominal_motor_torque_nm / 100.0

enable_tc = get_bool("ENABLE_TC")
tc_algorithm = next((name for symbol, name in (
    ("TC_ALGORITHM_PID", "pid"), ("TC_ALGORITHM_SMC", "smc"),
    ("TC_ALGORITHM_LEGACY", "legacy")) if get_bool(symbol)), "legacy")
tc_slip_ratio_limit = get_int("TC_SLIP_RATIO_LIMIT") / 1000.0
tc_torque_reduction_gain = get_int("TC_TORQUE_REDUCTION_GAIN")
tc_radius = get_int("TC_RADIUS_NM") / 1e9
tc_min_speed = get_int("TC_MIN_SPEED_MM_S") / 1000.0
tc_pid_kp = float(get_int("TC_PID_KP"))
tc_pid_ki = float(get_int("TC_PID_KI"))
tc_pid_kd = get_int("TC_PID_KD_MILLI") / 1000.0
tc_derivative_tau = get_int("TC_DERIVATIVE_TAU_MS") / 1000.0
tc_wheel_inertia = get_int("TC_WHEEL_INERTIA_MILLI") / 1000.0
tc_wheel_nm_per_unit = get_int("TC_WHEEL_NM_PER_UNIT_MILLI") / 1000.0
tc_observer_tau = get_int("TC_OBSERVER_TAU_MS") / 1000.0
tc_smc_gain = get_int("TC_SMC_GAIN_MILLI") / 1000.0
tc_smc_boundary = get_int("TC_SMC_BOUNDARY_MILLI") / 1000.0

ku_denominator = get_int("KU_DENOMINATOR")

if ku_denominator <= 0:
    raise ValueError("KU_DENOMINATOR must be greater than 0")

ku = 1.0 / ku_denominator

regen_braking_factor = get_int("REGEN_BRAKING_FACTOR") / 100.0


if min_torque > max_moment:
    raise ValueError("MIN_TORQUE cannot exceed MAX_MOMENT")

if tc_slip_ratio_limit <= 1.0:
    raise ValueError("TC_SLIP_RATIO_LIMIT must be > 1.0")

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
    tc_algorithm: {tc_algorithm}
    tc_slip_ratio_limit: {tc_slip_ratio_limit}
    tc_torque_reduction_gain: {float(tc_torque_reduction_gain)}
    tc_radius: {tc_radius}
    tc_min_speed: {tc_min_speed}
    tc_pid_kp: {tc_pid_kp}
    tc_pid_ki: {tc_pid_ki}
    tc_pid_kd: {tc_pid_kd}
    tc_derivative_tau: {tc_derivative_tau}
    tc_wheel_inertia: {tc_wheel_inertia}
    tc_wheel_nm_per_unit: {tc_wheel_nm_per_unit}
    tc_observer_tau: {tc_observer_tau}
    tc_smc_gain: {tc_smc_gain}
    tc_smc_boundary: {tc_smc_boundary}

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
