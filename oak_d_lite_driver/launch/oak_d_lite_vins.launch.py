"""Launch OAK-D Lite driver and VINS-Fusion together."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def get_vins_config():
    paths = [
        os.path.join(
            get_package_share_directory('vins'),
            'config', 'oak_d_lite', 'oak_d_lite_config.yaml'
        ),
        os.path.join(
            os.path.expanduser('~'),
            'ros2_ws/src/VINS-Fusion-ROS2/config/oak_d_lite/oak_d_lite_config.yaml'
        ),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]


def get_rviz_config():
    paths = [
        os.path.join(
            get_package_share_directory('vins'),
            'vins_rviz_config.rviz'
        ),
        os.path.join(
            os.path.expanduser('~'),
            'ros2_ws/src/VINS-Fusion-ROS2/config/vins_rviz_config.rviz'
        ),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]


def generate_launch_description():
    config = get_vins_config()
    rviz = get_rviz_config()

    oak_node = Node(
        package='oak_d_lite_driver',
        executable='oak_d_lite_node',
        name='oak_d_lite_driver',
        output='screen',
    )

    vins_node = Node(
        package='vins',
        executable='vins_node',
        name='vins_estimator',
        output='screen',
        arguments=[config],
    )

    loop_node = Node(
        package='loop_fusion',
        executable='loop_fusion_node',
        name='loop_fusion',
        output='screen',
        arguments=[config],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rvizvisualisation',
        output='log',
        arguments=['-d', rviz],
    )

    return LaunchDescription([oak_node, vins_node, loop_node, rviz_node])
