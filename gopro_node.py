import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
import subprocess
import threading
import socket
import time

class GoProNode(Node):
    def __init__(self):
        super().__init__('gopro_camera_node')
        self.publisher = self.create_publisher(Image, '/camera/camera/color/image_raw', qos_profile_sensor_data)
        self.gopro_ip = "172.27.188.51"
        cmd = [
            'ffmpeg',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-f', 'mpegts',
            '-i', 'udp://@0.0.0.0:8554?overrun_nonfatal=1&fifo_size=50000000',
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-s', '1920x1080',
            '-'
        ]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.running = True
        self.latest_frame = None
        self.lock = threading.Lock()
        
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.daemon = True
        
        self.publish_thread = threading.Thread(target=self.publish_loop)
        self.publish_thread.daemon = True
        
        self.keepalive_thread = threading.Thread(target=self.keepalive_loop)
        self.keepalive_thread.daemon = True
        
        self.capture_thread.start()
        self.publish_thread.start()
        self.keepalive_thread.start()

    def keepalive_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = b"_GPHD_:0:0:2:0.000000\n"
        while self.running and rclpy.ok():
            try:
                sock.sendto(message, (self.gopro_ip, 8554))
            except Exception:
                pass
            time.sleep(2.0)

    def capture_loop(self):
        frame_size = 1920 * 1080 * 3
        while self.running and rclpy.ok():
            raw_frame = b''
            while len(raw_frame) < frame_size and self.running:
                chunk = self.process.stdout.read(frame_size - len(raw_frame))
                if not chunk: break
                raw_frame += chunk
            if len(raw_frame) != frame_size:
                self.get_logger().error("FFMPEG stream broken")
                break
            with self.lock:
                self.latest_frame = raw_frame

    def publish_loop(self):
        frame_id = 0
        while self.running and rclpy.ok():
            frame_to_publish = None
            with self.lock:
                if self.latest_frame is not None:
                    frame_to_publish = self.latest_frame
                    self.latest_frame = None
            
            if frame_to_publish is not None:
                msg = Image()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = 'camera_color_optical_frame'
                msg.height, msg.width = 1080, 1920
                msg.encoding = 'rgb8'
                msg.is_bigendian = False
                msg.step = 1920 * 3
                # BYPASS Python's extremely slow array.array conversion for 6MB images!
                # By directly setting _data to the bytes object, we publish at 30 FPS instead of 2 FPS
                msg._data = frame_to_publish
                self.publisher.publish(msg)
                
                if frame_id % 30 == 0:
                    self.get_logger().info(f'Published frame {frame_id} at 1920x1080')
                frame_id += 1
            
            time.sleep(1.0 / 60.0) # Poll at 60Hz to catch 30fps frames

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()

def main(args=None):
    rclpy.init(args=args)
    node = GoProNode()
    try:
        while rclpy.ok():
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
