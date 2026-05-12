#!/bin/bash

NAMESPACE=${1:-/camera/camera/color}
echo "Starting Basler ROS2 Node in Docker container with namespace: $NAMESPACE ..."
docker exec -it ek_tag_detection_container bash -c "export ROS_DOMAIN_ID=55 && source /opt/ros/humble/setup.bash && python3 /workspace/camera_runner/basler_node.py $NAMESPACE"
