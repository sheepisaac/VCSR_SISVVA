# VCSR_SISVVA
Volumetric Capturing System using Robot: Subsystem for Immersive Scene Volumetric Video Acquisition
PLEASE! Check the shell script code and modify the directory pathes to customize for your local and remote server path.

SISVVA_autoACQ.sh:             Shell script for autonomously acquire the immersive scene multi-view image data set
SISVVA_autoGS.sh:              Shell script for autonomously estimate camera parameter of acquired image data set by SISVVA_autoACQ.sh and train immersive scene via 3DGS
realsense_save_image_ros.py:   Save image using ROS2-RealSense wrapper (please check this link: https://github.com/sheepisaac/ROS_RealSense_saveImageAndVideo)
ctrl_ugv.py:                   Control robot UGV motor (please check this link: https://github.com/sheepisaac/UGV_motor_control)
colmap_auto_isyang.py:         Estimate camera parameter from acquired image data via COLMAP Linux library

(Robot Local) SISVVA_autoACQ.sh
  └─ (Robot Local) realsense_save_image_ros.py
  └─ (Robot Local) ctrl_ugv.py
(Robot Local) SISVVA_autoGS.sh
  └─ (Remote Server) colmap_auto_isyang.py
      └─ (Remote Server) "COLMAP library" 
  └─ (Remote Server) "3DGS pipeline" convert.py
  └─ (Remote Server) "3DGS pipeline" train.py
  └─ (Remote Server) "3DGS pipeline" render.py
  └─ (Remote Server) "3DGS pipeline" metrics.py
