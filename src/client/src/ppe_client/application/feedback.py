from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    SYSTEM = "SYSTEM"
    POSE = "POSE"
    EMG = "EMG"


@dataclass(frozen=True)
class Feedback:
    type: FeedbackType
    message: str
