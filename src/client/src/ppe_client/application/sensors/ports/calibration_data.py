from dataclasses import dataclass
from enum import Enum


class ValueZone(Enum):
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"
    UNKNOWN = "Unknown"


@dataclass()
class CalibrationData:
    relaxed_values: list[float]
    tensed_values: list[float]
    low_threshold: float = 0.0
    mid_threshold: float = 0.0
    high_threshold: float = 0.0

    def zone_of(self, value: float) -> ValueZone:
        if value < self.low_threshold:
            return ValueZone.GREEN
        elif value < self.mid_threshold:
            return ValueZone.YELLOW
        else:
            return ValueZone.RED
