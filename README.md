# putm_ws
[![Build and Test](https://github.com/PUT-Motorsport/putm_ws/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/PUT-Motorsport/putm_ws/actions/workflows/build.yml)
Clone the repository with all the submodules
```bash
git clone --recurse-submodules git@github.com:PUT-Motorsport/putm_ws.git
```

Launch putm_controller and putm_vcl
```bash
ros2 launch launch/putm_ws.launch.py
```

Publish a message to the rtd topic
```bash
ros2 topic pub putm_vcl/rtd putm_vcl_interfaces/msg/Rtd "{state: 1}"
```

Publish a message to the frontbox_driver_input topic
```bash
ros2 topic pub -r 100 putm_vcl/frontbox_driver_input putm_vcl_interfaces/FrontboxDriverInput "{pedal_position: 0.5}"
```
