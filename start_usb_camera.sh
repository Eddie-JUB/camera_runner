#!/bin/bash
# This script launches a generic USB camera (e.g., webcam, Arducam) in the ROS2 environment.
# Topic names are remapped to match the existing RealSense pipeline without code modification.

# Takes video device as an argument; default is /dev/video0.
VIDEO_DEV=${1:-/dev/video0}
NAMESPACE=${2:-/camera/camera/color}

echo "Starting generic USB Camera node ($VIDEO_DEV) and mapping to $NAMESPACE/image_raw ..."
echo "Applying max FOV settings for Logitech Brio..."

# Launch the custom OpenCV camera node (supports MJPG 4K natively)
# NOTE: The 90-degree FOV lock is now handled inside brio_node.py AFTER ffmpeg starts!
docker exec -it ek_tag_detection_container bash -c "pkill -9 ffmpeg || true; export ROS_DOMAIN_ID=55 && source /opt/ros/humble/setup.bash && python3 /workspace/camera_runner/brio_node.py $VIDEO_DEV $NAMESPACE"
