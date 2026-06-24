from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    packages_to_launch = [
        ("putm_vcl", None),
        ("putm_controller", None),
        ("putm_lap_timer", None),
        ("xsens_mti_ros2_driver", "xsens_mti_node.launch.py"),
    ]
    
    ld = LaunchDescription()
    
    for pkg, launch_file in packages_to_launch:
        actual_launch_file = launch_file if launch_file else f"{pkg}.launch.py"
        
        ld.add_action(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare(pkg),
                        "launch",
                        actual_launch_file
                    ])
                )
            )
        )
        
    return ld