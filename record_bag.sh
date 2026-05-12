#!/bin/bash
echo "Recording bag file to: ./baggage_tag_data_d435i"
docker exec -it ek_tag_detection_container bash -c "source /opt/ros/humble/setup.bash && cd /workspace && ros2 bag record -o baggage_tag_data_d435i_2 /camera/camera/color/image_raw"
