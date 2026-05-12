#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
import cv2
import subprocess
import numpy as np

class PiCameraNode(Node):
    def __init__(self):
        super().__init__('pi_camera_node')
        
        # ROS2 publishers
        self.publisher_raw = self.create_publisher(Image, 'image_raw', 10)
        self.publisher_compressed = self.create_publisher(CompressedImage, 'image_raw/compressed', 10)
        self.bridge = CvBridge()

        self.udp_url = "udp://0.0.0.0:5000?overrun_nonfatal=1&fifo_size=50000000"
        self.get_logger().info(f"Opening Pi Camera UDP stream: {self.udp_url}")
        
        # Use OpenCV VideoCapture with FFMPEG backend for dynamic resolution support
        self.cap = cv2.VideoCapture(self.udp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Reduce latency

        self.timer = self.create_timer(0.01, self.capture_frame)
        self.get_logger().info("Pi Camera node started. Waiting for stream from Pi...")

    def capture_frame(self):
        try:
            if not self.cap.isOpened():
                self.cap.open(self.udp_url, cv2.CAP_FFMPEG)
                return

            ret, frame = self.cap.read()
            if not ret or frame is None:
                return

            # Publish Raw Image
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "pi_camera"
            self.publisher_raw.publish(msg)

            # Publish Compressed Image
            compressed_msg = self.bridge.cv2_to_compressed_imgmsg(frame)
            compressed_msg.header = msg.header
            self.publisher_compressed.publish(compressed_msg)

        except Exception as e:
            self.get_logger().error(f"Error capturing frame: {str(e)}")

def main(args=None):
    try:
        rclpy.init(args=args)
        node = PiCameraNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in pi_node: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
