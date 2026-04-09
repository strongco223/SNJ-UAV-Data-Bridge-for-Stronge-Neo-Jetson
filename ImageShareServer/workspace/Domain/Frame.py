from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Any

class Frame:
    def __init__(self, data: Any, frame_id: int, pts: int, timestamp_ns: int):
        self.data = data
        self.frame_id = frame_id
        self.pts = pts
        self.timestamp_ns = timestamp_ns