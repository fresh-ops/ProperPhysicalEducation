from ppe_client.domain import SensorDescriptor

from .ports import (
    CalibrationData,
    Sensor,
    SensorCalibrator,
    SensorRegistry,
)


class SensorService:
    def __init__(
        self,
        registry: SensorRegistry,
        calibrator: SensorCalibrator,
    ) -> None:
        self._registry = registry
        # TODO: remove connected sensors
        self._connected_sensors: dict[str, Sensor] = {}
        # TODO: remove calibration data
        self._calibration_data: dict[str, CalibrationData] = {}
        self._calibrator = calibrator

    def get_calibrator(self) -> SensorCalibrator:
        return self._calibrator

    def store_calibration(
        self, descriptor: SensorDescriptor, data: CalibrationData
    ) -> None:
        self._calibration_data[descriptor.identity] = data

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        return await self._registry.enumerate(timeout_s)

    # TODO: remove connection logic
    async def connect(self, descriptor: SensorDescriptor) -> bool:
        try:
            sensor = await self._registry.get(descriptor)
            await sensor.connect()
            self._connected_sensors[descriptor.identity] = sensor
            return sensor.has_connections()
        except Exception:
            return False

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        sensor = self._connected_sensors.get(descriptor.identity)
        if sensor is not None:
            await sensor.disconnect()
        self._connected_sensors.pop(descriptor.identity, None)
        if descriptor.identity in self._calibration_data:
            del self._calibration_data[descriptor.identity]

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        sensor = self._connected_sensors.get(descriptor.identity)
        return sensor.has_connections() if sensor is not None else False

    def get_sensor(self, descriptor: SensorDescriptor) -> Sensor | None:
        return self._connected_sensors.get(descriptor.identity)

    def get_all_connected(self) -> list[SensorDescriptor]:
        return [sensor.descriptor() for sensor in self._connected_sensors.values()]

    # TODO: remove calibration logic
    async def calibrate(
        self, descriptor: SensorDescriptor, duration_s: float = 5.0
    ) -> CalibrationData:
        calibrator = self.get_calibrator()
        sensor = self.get_sensor(descriptor)
        if not sensor:
            raise ValueError("No sensor for provided descriptor")
        data = await calibrator.calibrate(sensor, duration_s)
        self._calibration_data[descriptor.identity] = data
        return data

    # TODO: remove getters
    def get_calibration_data(
        self, descriptor: SensorDescriptor
    ) -> CalibrationData | None:
        return self._calibration_data.get(descriptor.identity)

    async def cleanup(self) -> None:
        for sensor in list(self._connected_sensors.values()):
            await sensor.disconnect()
        self._connected_sensors.clear()
        self._calibration_data.clear()
