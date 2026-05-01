from typing import Protocol

from .calibration_data import CalibrationData
from .sensor import Sensor


class SensorCalibrator(Protocol):
    async def calibrate(
        self, sensor: Sensor, duration_s: float = 5.0
    ) -> CalibrationData: ...

    def calculate_thresholds(self, data: CalibrationData) -> None: ...
