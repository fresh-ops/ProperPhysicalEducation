from abc import ABC, abstractmethod

from .sensor_session import SensorSession


class CalibrationData:
    def __init__(
        self,
        relaxed_values: list[float],
        tensed_values: list[float],
    ) -> None:
        self.relaxed_values = relaxed_values
        self.tensed_values = tensed_values
        self.low_threshold = 0.0
        self.mid_threshold = 0.0
        self.high_threshold = 0.0


class SensorCalibrator(ABC):
    @abstractmethod
    async def calibrate(
        self, session: SensorSession, duration_s: float = 5.0
    ) -> CalibrationData:
        pass

    @abstractmethod
    def calculate_thresholds(self, data: CalibrationData) -> None:
        pass

    @abstractmethod
    def get_zone(self, value: float, data: CalibrationData) -> str:
        pass
