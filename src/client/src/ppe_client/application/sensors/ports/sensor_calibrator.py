from abc import ABC, abstractmethod

from ppe_client.domain import SensorDescriptor


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
        self, descriptor: SensorDescriptor, duration_s: float = 5.0
    ) -> CalibrationData:
        pass

    @abstractmethod
    def calculate_thresholds(self, data: CalibrationData) -> None:
        pass

    @abstractmethod
    def get_zone(self, value: float, data: CalibrationData) -> str:
        pass
