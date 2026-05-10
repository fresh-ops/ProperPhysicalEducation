from dataclasses import dataclass

from .calibration.calibration_data import ValueZone


@dataclass(frozen=True, slots=True)
class SensorValue:
    data: float
    zone: ValueZone
    timestamp_ms: int
