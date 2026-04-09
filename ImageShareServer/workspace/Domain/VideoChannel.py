from abc import ABC, abstractmethod
from typing import Optional
from Domain.Frame import Frame


class VideoChannel(ABC):
    @abstractmethod
    def write(self, frame: Frame):
        pass

    @abstractmethod
    def read_latest(self) -> Optional[Frame]:
        pass