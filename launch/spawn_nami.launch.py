import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'nami_bot'
    
    # Expert Note: Relying on the dynamic share directory is ROS 2 best practice.
    # Fallback to absolute path used in dev workspace if package isn't fully installed.
    try:
        pkg_share = get_package_share_directory(package_name)
        urdf_file_path = os.path.join(pkg_share, 'urdf', 'nami.urdf')
    except:
        urdf_file_path = '/home/abdallah/nami_ws/src/nami_bot/urdf/nami.urdf'

    # 1. Start Gazebo Harmonic directly (Paused so you can watch her drop!)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', 'empty.sdf'],
        output='screen'
    )

    # 2. Spawn N.A.M.I. into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'nami', 
            '-file', urdf_file_path, 
            '-x', '0.0', 
            '-y', '0.0', 
            '-z', '0.1'
        ],
        output='screen'
    )

    # 3. THE NERVOUS SYSTEM: Bridge ROS 2 to Gazebo
    # Directional bridge `]` means ROS -> Gazebo (Twist messages flow into Sim)
# 3. THE NERVOUS SYSTEM: Bridge ROS 2 to Gazebo
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Topic @ ROS 2 Type ] Gazebo Type
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_entity,
        bridge
    ])