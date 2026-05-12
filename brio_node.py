import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from rclpy.qos import qos_profile_sensor_data
import subprocess

class BrioCameraNode(Node):
    def __init__(self, video_device, namespace='/camera/camera/color'):
        super().__init__('brio_camera_node')
        
        # Publish CompressedImage to completely bypass 25MB/frame network bottleneck
        topic_name = f'{namespace}/image_raw/compressed'
        self.publisher = self.create_publisher(CompressedImage, topic_name, qos_profile_sensor_data)
        
        self.get_logger().info(f"Opening camera via FFMPEG backend: {video_device}")
        
        cmd = [
            'ffmpeg', '-y', '-f', 'v4l2', '-input_format', 'mjpeg',
            '-video_size', '3840x2160', '-framerate', '30',
            '-i', video_device, '-c:v', 'copy', '-f', 'image2pipe', '-'
        ]
        
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            # Logitech Brio firmware resets FOV upon FFMPEG VIDIOC_S_FMT format negotiation!
            # We MUST forcefully apply the 90-degree FOV via UVC extension AFTER ffmpeg opens the device.
            self.get_logger().info("Applying 90-degree FOV hardware lock...")
            subprocess.Popen([
                'bash', '-c',
                f'sleep 1.5 && cd /workspace/cameractrls && ./cameractrls.py -d {video_device} -c logitech_brio_fov=90'
            ])
            
        except Exception as e:
            self.get_logger().error(f"Failed to start FFMPEG process: {e}")
            sys.exit(1)
            
        self.get_logger().info("Camera opened. Streaming native 4K MJPEG...")
            
        self.buffer = b''
        # Run capture loop much faster to drain pipe
        self.timer = self.create_timer(0.005, self.capture_frame)

    def capture_frame(self):
        if not self.proc or self.proc.poll() is not None:
            self.get_logger().error("FFMPEG process died.")
            sys.exit(1)
            
        # Read chunks from stdout
        chunk = self.proc.stdout.read(65536)
        if chunk:
            self.buffer += chunk
            
        # Extract full JPEG frames
        while True:
            start = self.buffer.find(b'\xff\xd8')
            if start == -1:
                break
            end = self.buffer.find(b'\xff\xd9', start)
            if end == -1:
                break
                
            # Exact JPEG frame
            jpg_data = self.buffer[start:end+2]
            self.buffer = self.buffer[end+2:]
            
            # Publish CompressedImage
            msg = CompressedImage()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "camera_color_optical_frame"
            msg.format = "jpeg"
            msg.data = jpg_data
            
            self.publisher.publish(msg)

def main(args=None):
    if len(sys.argv) < 2:
        print("Usage: python3 brio_node.py <video_device> [namespace]")
        sys.exit(1)
        
    video_device = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) > 2 else '/camera/camera/color'
    
    rclpy.init(args=args)
    node = BrioCameraNode(video_device, namespace)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(node, 'proc') and node.proc:
            node.proc.terminate()
            node.proc.wait()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
