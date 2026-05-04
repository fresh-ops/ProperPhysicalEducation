from typing import Protocol

from .calibration_data import CalibrationData


class SensorCalibrator(Protocol):
    def calibrate(
        self, tensed_data: list[float], relaxed_data: list[float]
    ) -> CalibrationData: ...
