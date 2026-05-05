import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():

    # THE FIX: Using the direct path so we don't have to compile the workspace yet
    urdf_file_path = '/home/abdallah/nami_ws/src/nami_bot/urdf/nami.urdf'

    # Read the URDF file into a text string
    with open(urdf_file_path, 'r') as infp:
        robot_description = infp.read()

    # 1. Start Gazebo Harmonic 
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', 'empty.sdf'],
        output='screen'
    )

    # 2. Spawn N.A.M.I. into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'nami', '-file', urdf_file_path, '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen'
    )

    # 3. THE NERVOUS SYSTEM: Bridge ROS 2 to Gazebo
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    # 4. SELF AWARENESS: Broadcast the robot's physical layout to ROS 2
    # 4. SELF AWARENESS: Broadcast the robot's physical layout to ROS 2
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,           # Sync to Matrix Time
            'publish_frequency': 50.0       # Fast TF broadcasts to keep SLAM tight
        }],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_entity,
        bridge,
        rsp_node
    ])