from abc import ABC, abstractmethod
from typing import Optional, Any
import numpy as np
import threading
import time

import gi
from gi.repository import GLib
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)


from Domain.Video import  VideoSource
from Domain.Frame import Frame

import os
os.environ["GST_DEBUG"] = "3"

class GstVideoSource(VideoSource):

    def __init__(self, device="/dev/video0", width=1280, height=720, fps=30, file_path="record.mkv"):
        self.file_path = file_path
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps

        self.pipeline = None
        self.appsink = None

        self._frame_id = 0
        self._latest_frame: Optional[Frame] = None
        self._lock = threading.Lock()

    def _build_pipeline(self):
        pipeline_str = (
                f"v4l2src device={self.device} ! "
                f"video/x-raw,format=UYVY,width={self.width},height={self.height} ! "
                f"videoconvert ! "
                f"tee name=t "

                # ===== appsink branch（raw RGB）=====
                f"t. ! queue ! "
                f"videoconvert ! video/x-raw,format=RGB ! "
                f"appsink name=sink emit-signals=true sync=false max-buffers=1 drop=true "

                # ===== encode once =====
                f"t. ! queue ! "
                f"x264enc bitrate=20000 tune=zerolatency ! "
                f"tee name=enc_t "

                # ===== recording =====
                f"enc_t. ! queue ! "
                f"matroskamux ! filesink location={self.file_path} "

                # ===== UDP streaming =====
                f"enc_t. ! queue ! "
                f"rtph264pay config-interval=1 pt=96 ! "
                f"udpsink host=192.168.144.120 port=20000"
        )

        print(pipeline_str)

        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")
        self.appsink.connect("new-sample", self._on_new_sample)

    def _add_bus_watch(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

    def _on_bus_message(self, bus, message):
        t = message.type

        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("\n=== GST ERROR ===")
            print("ERROR:", err)
            print("DEBUG:", debug)

        elif t == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print("\n=== GST WARNING ===")
            print("WARNING:", err)
            print("DEBUG:", debug)

        elif t == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old, new, pending = message.parse_state_changed()
                print(f"[STATE] {old.value_nick} → {new.value_nick}")

        elif t == Gst.MessageType.EOS:
            print("=== EOS ===")

    def _on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()

        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")

        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR


        try:
            data = np.frombuffer(map_info.data, dtype=np.uint8)
            frame_np = data.reshape((height, width, 3))
        finally:
            buf.unmap(map_info)

        pts = buf.pts
        timestamp_ns = time.monotonic_ns()

        with self._lock:
            self._frame_id += 1
            self._latest_frame = Frame(
                data=frame_np,
                frame_id=self._frame_id,
                pts=pts,
                timestamp_ns=timestamp_ns
            )

        return Gst.FlowReturn.OK
    
    def _start_loop(self):
        self.loop = GLib.MainLoop()
        self.loop_thread = threading.Thread(target=self.loop.run, daemon=True)
        self.loop_thread.start()

    # ===== Interface Implementation =====

    def start(self) -> None:
        self._build_pipeline()
        self._add_bus_watch()
        self._start_loop() 
        print(self.pipeline.set_state(Gst.State.PLAYING))

    def stop(self) -> None:
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

    def get_frame(self) -> Optional[Frame]:
        with self._lock:
            return self._latest_frame
