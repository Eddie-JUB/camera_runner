#!/bin/bash

# Default namespace is /pi
NAMESPACE=${1:-/pi}

echo "Starting Raspberry Pi Camera receiver node in namespace $NAMESPACE..."

# Function to check if a container is running
is_running() {
    docker ps --format '{{.Names}}' | grep -qw "$1"
}

if is_running "barcode_perception_container"; then
    TARGET_CONTAINER="barcode_perception_container"
elif is_running "ek_tag_detection_container"; then
    TARGET_CONTAINER="ek_tag_detection_container"
else
    echo "Error: No active container found. Please start the barcode_perception or camera_runner container first."
    exit 1
fi

echo "Using container: $TARGET_CONTAINER"

# Cleanup: Kill any lingering pi_node.py processes in the container to free UDP port 5000
docker exec "$TARGET_CONTAINER" /bin/bash -c "pkill -f pi_node.py || true"

# Small delay to ensure the OS frees the UDP port
sleep 1

# Run the node inside the docker container
docker exec -it "$TARGET_CONTAINER" /bin/bash -c "source /opt/ros/humble/setup.bash && python3 /workspace/camera_runner/pi_node.py --ros-args -r __ns:=$NAMESPACE"
