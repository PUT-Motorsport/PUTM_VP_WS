from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    current_topic_arg = DeclareLaunchArgument(
        'current_topic', default_value='/putm_vcl/current_sensor'
    )
    torque_topic_arg = DeclareLaunchArgument(
        'torque_topic', default_value='/putm_vcl/setpoints'
    )
    voltage_topic_arg = DeclareLaunchArgument(
        'voltage_topic', default_value='/putm_vcl/bms_hv_main'
    )
    n_lags_arg = DeclareLaunchArgument('n_lags', default_value='5')
    publish_rate_arg = DeclareLaunchArgument('publish_rate_hz', default_value='5.0')
    power_limit_arg = DeclareLaunchArgument('power_limit_w', default_value='80000.0')

    current_predictor_node = Node(
        package='current_predictor',
        executable='current_predictor_node',
        name='current_predictor',
        output='screen',
        parameters=[{
            'current_topic': LaunchConfiguration('current_topic'),
            'torque_topic': LaunchConfiguration('torque_topic'),
            'voltage_topic': LaunchConfiguration('voltage_topic'),
            'n_lags': LaunchConfiguration('n_lags'),
            'publish_rate_hz': LaunchConfiguration('publish_rate_hz'),
            'power_limit_w': LaunchConfiguration('power_limit_w'),
        }],
    )

    return LaunchDescription([
        current_topic_arg,
        torque_topic_arg,
        voltage_topic_arg,
        n_lags_arg,
        publish_rate_arg,
        power_limit_arg,
        current_predictor_node,
    ])