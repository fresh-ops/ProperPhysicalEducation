from dataclasses import dataclass
from enum import Enum, auto


class FrameOrigin(Enum):
    """Characterize the source of the frame."""

    CV2 = auto()


@dataclass(frozen=True, slots=True)
class Frame:
    """DTO that transfers raw data from camera."""

    raw: bytes
    shape: tuple[int, int, int]
    timestamp_ms: int
    origin: FrameOrigin
