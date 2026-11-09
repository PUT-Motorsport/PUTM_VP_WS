#!/usr/bin/env python3

from pathlib import Path
import kconfiglib

ROOT = Path(__file__).resolve().parent

kconf = kconfiglib.Kconfig(str(ROOT / "Kconfig"))
kconf.load_config(str(ROOT / ".config"))

if kconf.syms["CONTROL_MPC"].str_value == "y":
    control_system = "mpc"

elif kconf.syms["CONTROL_PID"].str_value == "y":
    control_system = "pid"

elif kconf.syms["CONTROL_OPEN_LOOP"].str_value == "y":
    control_system = "open_loop"

else:
    raise RuntimeError("No control system selected")

max_moment = int(kconf.syms["MAX_MOMENT"].str_value)

if not 0 <= max_moment <= 200:
    raise ValueError("MAX_MOMENT must be between 0 and 200")

output = ROOT / "config" / "vehicle.yaml"
output.parent.mkdir(parents=True, exist_ok=True)

yaml_content = f"""\
/**:
  ros__parameters:
    control_system: "{control_system}"
    max_moment: {max_moment}
"""

output.write_text(yaml_content)

print(f"Generated: {output}")
print(f"Control system: {control_system}")
print(f"Max moment: {max_moment} Nm")
