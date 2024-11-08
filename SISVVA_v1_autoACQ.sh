#!/usr/bin/expect -f

# Default value of parameter definition
set view_number 60
set sequence_name "default_sequence"
set left_motor 100
set right_motor 100

# Parameter value definition
foreach {flag value} $argv {
    if {$flag == "-vn"} {
        set view_number $value
    } elseif {$flag == "-sn"} {
        set sequence_name $value
    } elseif {$flag == "-lm"} {
        set left_motor $value
    } elseif {$flag == "-rm"} {
        set right_motor $value
    }
}

# Input parameter validation
puts "View number: $view_number"
puts "Sequence name: $sequence_name"
puts "Left motor power: $left_motor"
puts "Right motor power: $right_motor"

# 1. Using nohup, run ROS and RealSense nodes in the background
puts "Activating ROS and RealSense nodes in the background using nohup..."
exec nohup bash -c "source /opt/ros/foxy/setup.bash && ros2 launch realsense2_camera rs_launch.py" > realsense_launch.log 2>&1 &

# 2. Directory for storing results
set results_dir "/home/vcrobot3/robot_ws/Results/$sequence_name" # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
exec mkdir -p $results_dir
puts "Results directory created: $results_dir"

# 3. Control robot movement and image acquisition operation
puts "Starting robot movement and image acquisition..."

for {set i 0} {$i < $view_number} {incr i} {
    # Image capture script
    puts "Frame number: $i, saving image..."
    spawn python3 /home/vcrobot3/robot_ws/realsense_save_image_ros.py # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
    expect "Enter the frame number: "
    send "$i\r"
    sleep 1

    # Robot movement control script
    puts "Moving robot, left motor: $left_motor, right motor: $right_motor"
    spawn python3 /home/vcrobot3/robot_ws/ctrl_ugv.py # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
    expect "Enter command:"
    send "go $left_motor $right_motor\r"
    sleep 1
    send "stop\r"
    sleep 1
    send "quit\r"
}

# Termination
puts "Task completed!"
expect eof
