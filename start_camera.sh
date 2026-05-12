#!/bin/bash
docker exec -it ek_tag_detection_container bash -c "source /opt/ros/humble/setup.bash && ros2 launch realsense2_camera rs_launch.py align_depth.enable:=true"
