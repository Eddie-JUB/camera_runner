#!/bin/bash

# GoPro Hero 8 Webcam Mode IP
GOPRO_IP="172.27.188.51"

echo "Sending STOP command to clear any frozen streams..."
curl -s "http://$GOPRO_IP/gp/gpWebcam/STOP" > /dev/null
sleep 2

echo "Activating GoPro Hero 8 Webcam Stream at 1080p (Highest Resolution)..."
# The ?res=1080 parameter requests 1080p stream
curl -s "http://$GOPRO_IP/gp/gpWebcam/START?res=1080" > /dev/null

echo "Waiting for stream to initialize..."
sleep 3

echo "Starting GoPro ROS2 Node in Docker container..."
docker exec -it ek_tag_detection_container bash -c "export ROS_DOMAIN_ID=55 && source /opt/ros/humble/setup.bash && python3 /workspace/camera_runner/gopro_node.py"
