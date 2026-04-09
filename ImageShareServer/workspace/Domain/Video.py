from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Any
from Domain.Frame import Frame


class VideoSource(ABC):

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_frame(self) -> Optional[Frame]:
        pass