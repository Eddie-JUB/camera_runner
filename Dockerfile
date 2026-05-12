FROM osrf/ros:humble-desktop

# Install base packages and RealSense ROS2 packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3-pip \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-description \
    ros-humble-rviz2 \
    ros-humble-rosbag2 \
    ros-humble-rosbag2-storage-mcap \
    ros-humble-v4l2-camera \
    ros-humble-image-transport-plugins \
    ros-humble-rqt-image-view \
    ros-humble-rqt-common-plugins \
    v4l-utils \
    libzbar0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for the barcode detection pipeline (YOLO, etc.)
RUN pip3 install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install opencv-python ultralytics "numpy<2" huggingface_hub pyzbar pypylon tensorrt-cu11

WORKDIR /workspace
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
ENV ROS_DOMAIN_ID=55
