from dataclasses import dataclass
from enum import Enum


class ValueZone(Enum):
    GREEN = "Green"
    YELLOW = "Yellow"
    RED = "Red"
    UNKNOWN = "Unknown"


@dataclass()
class CalibrationData:
    low_threshold: float
    mid_threshold: float
    high_threshold: float

    def zone_of(self, value: float) -> ValueZone:
        if value < self.low_threshold:
            return ValueZone.GREEN
        elif value < self.mid_threshold:
            return ValueZone.YELLOW
        else:
            return ValueZone.RED
