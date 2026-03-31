from dataclasses import dataclass


class FeedbackType:
    SYSTEM = "SYSTEM"
    POSE = "POSE"


@dataclass
class Feedback:
    type: str
    message: str
