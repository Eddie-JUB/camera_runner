# Camera Runner 📸

A unified, containerized ROS 2 camera acquisition system designed to support a wide range of camera hardware. It standardizes the input streams from various devices (RealSense, Basler, GoPro, Raspberry Pi, Generic USB) into standard ROS 2 `sensor_msgs/Image` and `sensor_msgs/CompressedImage` topics, acting as the universal frontend for downstream perception tasks (like `barcode_perception`).

---

## 🚀 Key Features

- **Multi-Camera Support**: Seamlessly interfaces with diverse camera hardware:
  - Intel RealSense (via `realsense-ros`)
  - Basler Industrial Cameras (via PyPylon)
  - GoPro Cameras
  - Raspberry Pi Cameras (via low-latency UDP streams)
  - Generic USB Cameras / Logitech Brio (with high-res MJPG/FFMPEG support)
- **Containerized Environment**: Full Docker and `docker-compose` support with GPU passthrough, ensuring dependency isolation and cross-platform consistency.
- **Unified Output Topics**: Regardless of the camera source, images are mapped to standardized namespaces (e.g., `/camera/camera/color/image_raw`), allowing perception nodes to remain hardware-agnostic.
- **Integrated Tooling**: Built-in scripts for camera calibration (`run_calibration.sh`), bag recording (`record_bag.sh`), and RViz visualization (`run_rviz.sh`).

---

## 📂 Directory Structure

```
camera_runner/
├── Dockerfile                  # Base ROS2 Humble + Camera Driver Image
├── docker-compose.yml          # Container configuration (Networking, GPU, Volumes)
├── basler_node.py              # Basler camera ROS2 node
├── brio_node.py                # Generic USB / Logitech Brio ROS2 node
├── gopro_node.py               # GoPro ROS2 node
├── pi_node.py                  # Raspberry Pi UDP receiver ROS2 node
├── start_basler.sh             # Launch script for Basler
├── start_camera.sh             # Launch script for Intel RealSense
├── start_gopro.sh              # Launch script for GoPro
├── start_pi_camera.sh          # Launch script for Raspberry Pi UDP stream
├── start_usb_camera.sh         # Launch script for USB webcams
├── run_calibration.sh          # Intrinsic/Extrinsic camera calibration script
├── run_rviz.sh                 # RViz2 visualization shortcut
└── record_bag.sh               # ROS2 bag recording script
```

---

## 🛠️ Installation & Setup

1. **Build and start the Docker container:**
   ```bash
   docker compose up -d --build
   ```
   *For Jetson (ARM64) users, export the Dockerfile extension before running:*
   ```bash
   export DOCKERFILE_EXT=".jetson"
   docker compose up -d --build
   ```
2. **Verify container status:**
   Make sure `ek_tag_detection_container` is running.

---

## 🎬 Launching Cameras

Each camera type has a dedicated launch script that handles the necessary environment variables and executes the corresponding ROS 2 node inside the container.

### Intel RealSense
Starts the standard `realsense2_camera` node.
```bash
./start_camera.sh
```

### Generic USB Camera / Logitech Brio
Starts a high-resolution OpenCV/FFMPEG based node. You can optionally specify the `/dev/videoX` device.
```bash
./start_usb_camera.sh /dev/video0
```

### Basler Camera
Initializes PyPylon to capture frames from connected Basler industrial cameras.
```bash
./start_basler.sh
```

### Raspberry Pi Camera (UDP Stream)
Listens for an incoming UDP stream (usually on port 5000) broadcasted from a Raspberry Pi.
```bash
./start_pi_camera.sh
```

### GoPro Camera
Connects to a GoPro video stream and wraps it into a ROS 2 topic.
```bash
./start_gopro.sh
```

---

## 🔧 Utilities

- **Visualization:**
  To quickly view the incoming camera feed:
  ```bash
  ./run_rviz.sh
  ```
- **Recording Data:**
  To record a ROS 2 bag file of the current camera stream (useful for offline testing or benchmarking):
  ```bash
  ./record_bag.sh
  ```
- **Calibration:**
  To run the camera calibrator node for obtaining intrinsic camera parameters (supports standard and fisheye lenses):
  ```bash
  ./run_calibration.sh
  ```

---

## ⚙️ Configuration

By default, the `docker-compose.yml` sets the `ROS_DOMAIN_ID` to **55**. If your network uses a different domain ID, be sure to update it in the `docker-compose.yml` and restart the container. All launch scripts dynamically export this domain ID before spinning up the nodes.
