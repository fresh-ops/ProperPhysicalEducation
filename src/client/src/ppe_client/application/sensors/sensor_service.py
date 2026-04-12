from typing import TYPE_CHECKING

from wireup import injectable

from ppe_client.adapters.sensors.bleak_sensor_connector import BleakSensorConnector
from ppe_client.adapters.sensors.bleak_sensor_enumerator import BleakSensorEnumerator
from ppe_client.application.sensors.ports.sensor_calibrator import CalibrationData
from ppe_client.domain import SensorDescriptor

if TYPE_CHECKING:
    from ppe_client.adapters.sensors.bleak_sensor_calibrator import (
        BleakSensorCalibrator,
    )
    from ppe_client.application.sensors.ports.sensor_session import SensorSession


@injectable
class SensorService:
    def __init__(
        self, enumerator: BleakSensorEnumerator, connector: BleakSensorConnector
    ) -> None:
        self._enumerator = enumerator
        self._connector = connector
        self._connected_sensors: dict[str, SensorDescriptor] = {}
        self._calibration_data: dict[str, CalibrationData] = {}
        self._calibrator: BleakSensorCalibrator | None = None

    def _get_calibrator(self) -> "BleakSensorCalibrator":
        if self._calibrator is None:
            from ppe_client.adapters.sensors.bleak_sensor_calibrator import (
                BleakSensorCalibrator,
            )

            self._calibrator = BleakSensorCalibrator(self)
        return self._calibrator

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

    def get_session(self, descriptor: SensorDescriptor) -> "SensorSession | None":
        return self._connector.get_session(descriptor)

    def get_all_connected(self) -> list[SensorDescriptor]:
        return list(self._connected_sensors.values())

    async def calibrate(
        self, descriptor: SensorDescriptor, duration_s: float = 5.0
    ) -> CalibrationData:
        calibrator = self._get_calibrator()
        data = await calibrator.calibrate(descriptor, duration_s)
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
        calibrator = self._get_calibrator()
        return calibrator.get_zone(value, data)

    async def cleanup(self) -> None:
        await self._connector.cleanup()
        self._connected_sensors.clear()
        self._calibration_data.clear()
