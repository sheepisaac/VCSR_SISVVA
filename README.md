# VCSR_SISVVA 
Volumetric Capturing System using Robot: Subsystem for Immersive Scene Volumetric Video Acquisition <br/>
<ins> **PLEASE! Check the shell script code and modify the directory pathes to customize for your local and remote server path!** </ins> <br/>
<br/>
<ins> **SISVVA_autoACQ.sh** </ins>: Shell script for autonomously acquire the immersive scene multi-view image data set <br/>
<ins> **SISVVA_autoGS.sh** </ins>: Shell script for autonomously estimate camera parameter of acquired image data set by SISVVA_autoACQ.sh and train immersive scene via 3DGS <br/>
<ins> **realsense_save_image_ros.py** </ins>: Save image using ROS2-RealSense wrapper (please check this [link](https://github.com/sheepisaac/ROS_RealSense_saveImageAndVideo)) <br/>
<ins> **ctrl_ugv.py** </ins>: Control robot UGV motor (please check this [link](https://github.com/sheepisaac/UGV_motor_control)) <br/>
<ins> **colmap_auto_isyang.py** </ins>: Estimate camera parameter from acquired image data via COLMAP Linux library <br/>
 <br/>
(Robot Local) SISVVA_autoACQ.sh <br/>
  └─ (Robot Local) realsense_save_image_ros.py <br/>
  └─ (Robot Local) ctrl_ugv.py <br/>
(Robot Local) SISVVA_autoGS.sh <br/>
  └─ (Remote Server) colmap_auto_isyang.py <br/>
      └─ (Remote Server) "COLMAP library"  <br/>
  └─ (Remote Server) "3DGS pipeline" convert.py <br/>
  └─ (Remote Server) "3DGS pipeline" train.py <br/>
  └─ (Remote Server) "3DGS pipeline" render.py <br/>
  └─ (Remote Server) "3DGS pipeline" metrics.py <br/>
