#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

export MENUCONFIG_STYLE="\
path=fg:white,bg:black \
separator=fg:blue,bg:black \
list=fg:white,bg:black \
selection=fg:black,bg:brightwhite,bold \
inv-list=fg:brightblack,bg:black \
inv-selection=fg:white,bg:blue \
help=fg:white,bg:black \
show-help=fg:white,bg:black \
frame=fg:blue,bg:black \
body=fg:white,bg:black \
edit=fg:brightwhite,bg:black \
jump-edit=fg:brightwhite,bg:black \
text=fg:white,bg:black"

menuconfig Kconfig

if [[ -f .config ]]; then
    echo "Generating ROS 2 configuration..."
    python3 generate_config.py
else
    echo "Configuration not found"
    exit 1
fi
