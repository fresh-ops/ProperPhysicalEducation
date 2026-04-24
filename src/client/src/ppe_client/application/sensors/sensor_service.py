from ppe_client.domain import SensorDescriptor

from .ports import (
    CalibrationData,
    SensorCalibrator,
    SensorConnector,
    SensorEnumerator,
    SensorSession,
)


class SensorService:
    def __init__(
        self,
        enumerator: SensorEnumerator,
        connector: SensorConnector,
        calibrator: SensorCalibrator,
    ) -> None:
        self._enumerator = enumerator
        self._connector = connector
        self._connected_sensors: dict[str, SensorDescriptor] = {}
        self._calibration_data: dict[str, CalibrationData] = {}
        self._calibrator = calibrator

    def get_calibrator(self) -> SensorCalibrator:
        return self._calibrator

    def store_calibration(
        self, descriptor: SensorDescriptor, data: CalibrationData
    ) -> None:
        self._calibration_data[descriptor.identity] = data

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        return await self._enumerator.discover(timeout_s)

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        success = await self._connector.connect(descriptor)
        if success:
            self._connected_sensors[descriptor.identity] = descriptor
        return success

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        await self._connector.disconnect(descriptor)
        self._connected_sensors.pop(descriptor.identity, None)
        if descriptor.identity in self._calibration_data:
            del self._calibration_data[descriptor.identity]

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        return self._connector.is_connected(descriptor)

    def get_session(self, descriptor: SensorDescriptor) -> SensorSession | None:
        return self._connector.get_session(descriptor)

    def get_all_connected(self) -> list[SensorDescriptor]:
        return list(self._connected_sensors.values())

    async def calibrate(
        self, descriptor: SensorDescriptor, duration_s: float = 5.0
    ) -> CalibrationData:
        calibrator = self.get_calibrator()
        session = self.get_session(descriptor)
        if not session:
            raise ValueError("No session for provided sensor")
        data = await calibrator.calibrate(session, duration_s)
        self._calibration_data[descriptor.identity] = data
        return data

    def get_calibration_data(
        self, descriptor: SensorDescriptor
    ) -> CalibrationData | None:
        return self._calibration_data.get(descriptor.identity)

    def get_zone(self, descriptor: SensorDescriptor, value: float) -> str:
        data = self.get_calibration_data(descriptor)
        if not data:
            return "unknown"
        calibrator = self.get_calibrator()
        return calibrator.get_zone(value, data)

    async def cleanup(self) -> None:
        await self._connector.cleanup()
        self._connected_sensors.clear()
        self._calibration_data.clear()
