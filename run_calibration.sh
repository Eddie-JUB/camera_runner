#!/bin/bash
# Official ROS 2 Camera Calibration Launcher (Patched for Fisheye ChArUco)
# Make sure your container is running (e.g. docker compose up -d)

docker exec -it ek_tag_detection_container bash -c "
    export ROS_DOMAIN_ID=55 &&
    source /opt/ros/humble/setup.bash &&
    export PYTHONPATH=/workspace:\$PYTHONPATH &&
    python3 /workspace/cameracalibrator.py \\
        --size 5x5 \\
        --square 0.11 \\
        --pattern charuco \\
        --charuco_marker_size 0.082 \\
        --aruco_dict 6x6_250 \\
        --no-service-check \\
        --camera_name fisheye_cam \\
        image:=/camera/camera/color/image_raw
"
