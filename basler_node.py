#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
import pypylon.pylon as py
import time

class BaslerNode(Node):
    def __init__(self, namespace='/camera/camera/color'):
        super().__init__('basler_camera_node')
        topic_name = f'{namespace}/image_raw'
        self.publisher = self.create_publisher(Image, topic_name, qos_profile_sensor_data)
        
        # Connect to the first available Basler camera
        try:
            self.camera = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
            self.get_logger().info(f"Using device: {self.camera.GetDeviceInfo().GetModelName()}")
        except Exception as e:
            self.get_logger().error(f"Failed to find Basler camera: {e}")
            sys.exit(1)

        self.camera.Open()
        
        # Optional: Set resolution to 1080p if 4K is too heavy, but we'll stream at native resolution
        # self.camera.Width.Value = 1920
        # self.camera.Height.Value = 1080
        
        self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly)
        self.converter = py.ImageFormatConverter()
        
        # Converting to RGB8 format so it's compatible with ROS 2 and OpenCV
        self.converter.OutputPixelFormat = py.PixelType_RGB8packed
        self.converter.OutputBitAlignment = py.OutputBitAlignment_MsbAligned
        
        self.running = True

    def stop(self):
        self.running = False
        if self.camera.IsGrabbing():
            self.camera.StopGrabbing()
        if self.camera.IsOpen():
            self.camera.Close()

def main(args=None):
    namespace = sys.argv[1] if len(sys.argv) > 1 else '/camera/camera/color'
    rclpy.init(args=args)
    node = BaslerNode(namespace)
    
    frame_id = 0
    try:
        # Run capture and publish loop in the main thread to avoid ROS2 GIL contention!
        while node.running and rclpy.ok() and node.camera.IsGrabbing():
            try:
                grabResult = node.camera.RetrieveResult(5000, py.TimeoutHandling_ThrowException)
            except py.TimeoutException:
                node.get_logger().warn("Camera read timeout")
                continue

            if grabResult.GrabSucceeded():
                # Convert the image to RGB8
                image = node.converter.Convert(grabResult)
                img_np = image.GetArray()
                height, width, _ = img_np.shape
                
                # Convert to raw bytes
                raw_bytes = img_np.tobytes()

                msg = Image()
                msg.header.stamp = node.get_clock().now().to_msg()
                msg.header.frame_id = 'camera_color_optical_frame'
                msg.height = height
                msg.width = width
                msg.encoding = 'rgb8'
                msg.is_bigendian = False
                msg.step = width * 3
                
                # BYPASS Python's extremely slow array.array conversion for high-res images!
                msg._data = raw_bytes
                
                node.publisher.publish(msg)
                
                if frame_id % 30 == 0:
                    node.get_logger().info(f'Published frame {frame_id} at {width}x{height}')
                frame_id += 1
                
            grabResult.Release()
            
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
