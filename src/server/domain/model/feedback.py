from dataclasses import dataclass


@dataclass
class Feedback:
    type: str
    message: str
