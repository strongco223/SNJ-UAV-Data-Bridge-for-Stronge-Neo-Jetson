from Infra.GstVideoSource import GstVideoSource
from Infra.ShmVideoChannel import ShmVideoChannel

import time, os
from datetime import datetime
import threading
from PIL import Image

class ObjContainer:
    def __init__(self):
        self.run_dir = self.create_run_dir()
        self.videosource: VideoSource = GstVideoSource(file_path=f"{self.run_dir}/record.mkv")
        self.videochannel: VideoChannel = ShmVideoChannel()

    def create_run_dir(self,base_path="Data"):
        now = datetime.now()
        folder_name = now.strftime("%Y%m%d_%H%M%S")  # 20260326_104512
        path = os.path.join(base_path, folder_name)
        os.makedirs(path, exist_ok=True)
        return path


def video_worker(videosource, videochannel):
    videosource.start()

    last_frame_id = -1

    while True:
        frame = videosource.get_frame()
        if frame is None:
            time.sleep(0.001)
            continue

        if frame.frame_id == last_frame_id:
            continue

        last_frame_id = frame.frame_id
        videochannel.write(frame)
        print(f"frame_id={frame.frame_id}, ts={frame.timestamp_ns}")


def consumer_worker(videochannel, save_dir="output"):
    os.makedirs(save_dir, exist_ok=True)

    last_frame_id = -1

    while True:
        frame = videochannel.read_latest()
        if frame is None:
            time.sleep(0.005)
            continue

        if frame.frame_id == last_frame_id:
            continue

        last_frame_id = frame.frame_id

        print(f"frame_id={frame.frame_id}, ts={frame.timestamp_ns}")

        filename = os.path.join(save_dir, f"{frame.frame_id}.jpg")

        try:
            # 假設 frame.data 是 numpy array (H, W, 3)
            img = Image.fromarray(frame.data)
            img.save(filename)
        except Exception as e:
            print(f"save failed: {e}")

def main():
    obj_container = ObjContainer()

    videosource = obj_container.videosource
    videochannel = obj_container.videochannel

    t1 = threading.Thread(
        target=video_worker,
        args=(videosource, videochannel),
        daemon=True
    )

    t2 = threading.Thread(
        target=consumer_worker,
        args=(videochannel, "output"),
        daemon=True
    )

    t1.start()
    #t2.start()
    t1.join()
    #t2.join()

if __name__ == "__main__":
    main()