from dataclasses import dataclass
from typing import Protocol

from .sensor_session import SensorSession


@dataclass()
class CalibrationData:
    relaxed_values: list[float]
    tensed_values: list[float]
    low_threshold: float = 0.0
    mid_threshold: float = 0.0
    high_threshold: float = 0.0


class SensorCalibrator(Protocol):
    async def calibrate(
        self, session: SensorSession, duration_s: float = 5.0
    ) -> CalibrationData: ...

    def calculate_thresholds(self, data: CalibrationData) -> None: ...

    def get_zone(self, value: float, data: CalibrationData) -> str: ...
