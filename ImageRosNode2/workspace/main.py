import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import time,os
from datetime import datetime
import numpy as np

from Infra.ShmVideoChannel import ShmVideoChannel

class ObjContainer:
    def __init__(self):
        self.run_dir = self.create_run_dir()
        self.videochannel: VideoChannel = ShmVideoChannel()

    def create_run_dir(self,base_path="Data"):
        now = datetime.now()
        folder_name = now.strftime("%Y%m%d_%H%M%S")  # 20260326_104512
        path = os.path.join(base_path, folder_name)
        os.makedirs(path, exist_ok=True)
        return path

class VideoPublisher(Node):
    def __init__(self, videochannel):
        super().__init__('video_publisher')
        self.videochannel = videochannel
        self.pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.last_frame_id = -1

        self.timer = self.create_timer(0.01, self.loop)  # 100Hz

    def loop(self):
        frame = self.videochannel.read_latest()
        if frame is None:
            return

        if frame.frame_id == self.last_frame_id:
            return
        self.last_frame_id = frame.frame_id
        
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()

        h, w, c = frame.data.shape
        msg.height = h
        msg.width = w
        msg.encoding = 'rgb8'
        msg.step = w * c

        frame_data = np.array(frame.data, copy=True)
        t1  = time.time()
        
        bytes_frame = frame_data.tobytes()
        
        t2 = time.time()

        msg.data = bytearray(bytes_frame)
        print(f"Reshape and memoryview time: {t2 - t1:.4f} seconds")

        #self.pub.publish(msg)
        
        print(f"Published frame_id: {frame.frame_id}")


def main():
    obj_container = ObjContainer()
    videochannel = obj_container.videochannel

    rclpy.init()

    node = VideoPublisher(videochannel)
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()