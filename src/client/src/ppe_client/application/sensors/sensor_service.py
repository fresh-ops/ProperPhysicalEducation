from ppe_client.domain import SensorDescriptor

from .calibration import SensorCalibrator
from .ports import (
    Sensor,
    SensorRegistry,
)


class SensorService:
    def __init__(
        self,
        registry: SensorRegistry,
        calibrator: SensorCalibrator,
    ) -> None:
        self._registry = registry
        self._calibrator = calibrator

    def get_calibrator(self) -> SensorCalibrator:
        return self._calibrator

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        return await self._registry.enumerate(timeout_s)

    async def get_sensor(self, descriptor: SensorDescriptor) -> Sensor:
        return await self._registry.get(descriptor)
