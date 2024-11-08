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

# 1. nohup을 사용하여 백그라운드에서 ROS와 리얼센스 노드 실행
puts "nohup을 사용하여 백그라운드에서 ROS와 리얼센스 노드를 활성화합니다..."
exec nohup bash -c "source /opt/ros/foxy/setup.bash && ros2 launch realsense2_camera rs_launch.py" > realsense_launch.log 2>&1 &

# 2. Directory for storing results
set results_dir "/home/vcrobot3/robot_ws/Results/$sequence_name" # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
exec mkdir -p $results_dir
puts "결과 디렉토리 생성됨: $results_dir"

# 3. Control robot movement and image acquisition operation
puts "로봇 이동 및 이미지 취득을 시작합니다..."

for {set i 0} {$i < $view_number} {incr i} {
    # Image capture script
    puts "프레임 번호: $i, 이미지 저장 중..."
    spawn python3 /home/vcrobot3/robot_ws/realsense_save_image_ros.py # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
    expect "Enter the frame number: "
    send "$i\r"
    sleep 1
    
    # Robot movement control script
    puts "로봇 이동 중, 왼쪽 모터: $left_motor, 오른쪽 모터: $right_motor"
    spawn python3 /home/vcrobot3/robot_ws/ctrl_ugv.py # SET_TO_YOUR_ROBOT_MICROPROCESSOR_LOCAL_PATH
    expect "Enter command:"
    send "go $left_motor $right_motor\r"
    sleep 1
    send "stop\r"
    sleep 1
    send "quit\r"
}

# 종료
puts "작업 완료!"
expect eof
