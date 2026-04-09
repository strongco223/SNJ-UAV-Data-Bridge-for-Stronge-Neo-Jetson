# infra/shm_video_channel.py
import threading
from typing import Optional, List

# Infra/ShmVideoChannel.py
import os
import mmap
import struct
import numpy as np

from Domain.Frame import Frame
from Domain.VideoChannel import VideoChannel


# ---- config ----
SLOT_COUNT = 30
MAX_FRAME_BYTES = 1920 * 1080 * 3

GLOBAL_HEADER_FORMAT = "I"   # write_index
GLOBAL_HEADER_SIZE = struct.calcsize(GLOBAL_HEADER_FORMAT)

SLOT_HEADER_FORMAT = "IIIII"  
# seq, frame_id, width, height, size
SLOT_HEADER_SIZE = struct.calcsize(SLOT_HEADER_FORMAT)

SLOT_SIZE = SLOT_HEADER_SIZE + MAX_FRAME_BYTES
TOTAL_SIZE = GLOBAL_HEADER_SIZE + SLOT_SIZE * SLOT_COUNT


class ShmVideoChannel(VideoChannel):
    def __init__(self, name="/video_shm"):
        path = f"/dev/shm{name}"

        exists = os.path.exists(path)
        self.fd = open(path, "r+b" if exists else "w+b")

        if not exists:
            self.fd.truncate(TOTAL_SIZE)

        self.mm = mmap.mmap(self.fd.fileno(), TOTAL_SIZE)

    # ---------------- writer ----------------
    def write(self, frame: Frame):
        write_index = struct.unpack_from("I", self.mm, 0)[0]

        slot = write_index % SLOT_COUNT
        base = GLOBAL_HEADER_SIZE + slot * SLOT_SIZE

        h, w, _ = frame.data.shape
        data = frame.data.tobytes()
        size = len(data)

        if size > MAX_FRAME_BYTES:
            return

        # read seq
        seq = struct.unpack_from("I", self.mm, base)[0]

        # write begin
        struct.pack_into("I", self.mm, base, seq + 1)

        # write header
        struct.pack_into(
            SLOT_HEADER_FORMAT,
            self.mm,
            base,
            seq + 1,
            frame.frame_id,
            w,
            h,
            size
        )

        # write data
        self.mm[base + SLOT_HEADER_SIZE : base + SLOT_HEADER_SIZE + size] = data

        # write end
        struct.pack_into("I", self.mm, base, seq + 2)

        # update global write_index（最後寫，避免 reader 提前看到）
        struct.pack_into("I", self.mm, 0, write_index + 1)

    # ---------------- reader ----------------
    def read_latest(self):
        write_index = struct.unpack_from("I", self.mm, 0)[0]

        if write_index == 0:
            return None

        slot = (write_index - 1) % SLOT_COUNT
        base = GLOBAL_HEADER_SIZE + slot * SLOT_SIZE

        while True:
            seq1 = struct.unpack_from("I", self.mm, base)[0]

            if seq1 % 2 == 1:
                continue  # writer in progress

            header = struct.unpack_from(SLOT_HEADER_FORMAT, self.mm, base)
            _, frame_id, w, h, size = header

            if size == 0 or size > MAX_FRAME_BYTES:
                return None

            data = self.mm[
                base + SLOT_HEADER_SIZE : base + SLOT_HEADER_SIZE + size
            ]

            seq2 = struct.unpack_from("I", self.mm, base)[0]

            if seq1 == seq2:
                arr = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 3))
                return Frame(arr, frame_id, 0, 0)