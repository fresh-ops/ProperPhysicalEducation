import struct

from bleak import BleakClient

from ppe_client.application.sensors.ports import (
    CalibrationData,
    SensorCalibrator,
    ValueZone,
)
from ppe_client.domain import SensorDescriptor


class BleakSensor:
    """An adapter for the BleakClient"""

    _CHARACTERISTIC_UUID = "0000503f-0000-1000-8000-00805f9b34fb"

    _client: BleakClient
    _descriptor: SensorDescriptor
    _connections_count: int
    _calibrator: SensorCalibrator | None
    _calibration_data: CalibrationData | None

    def __init__(
        self,
        descriptor: SensorDescriptor,
        calibrator: SensorCalibrator | None = None,
    ) -> None:
        self._client = BleakClient(descriptor.address)
        self._descriptor = descriptor
        self._connections_count = 0
        self._calibrator = calibrator
        self._calibration_data = None

    async def connect(self) -> None:
        if self._connections_count == 0:
            await self._client.connect()
        self._connections_count += 1

    async def disconnect(self) -> None:
        if self._connections_count == 0:
            return
        self._connections_count -= 1
        if self._connections_count == 0:
            await self._client.disconnect()

    def descriptor(self) -> SensorDescriptor:
        return self._descriptor

    def has_connections(self) -> bool:
        return self._connections_count > 0

    async def read(self) -> float:
        raw_data = await self._client.read_gatt_char(self._CHARACTERISTIC_UUID)
        return float(struct.unpack("f", raw_data)[0])

    async def read_with_zone(self) -> tuple[float, ValueZone]:
        value = await self.read()
        if not self._calibration_data:
            return value, ValueZone.UNKNOWN
        return value, self._calibration_data.zone_of(value)

    async def calibrate(
        self, duration_s: float = 5.0, apply: bool = True
    ) -> CalibrationData:
        if self._calibrator is None:
            raise RuntimeError("No calibrator available for this sensor")

        data = await self._calibrator.calibrate(self, duration_s)
        if apply:
            self.apply_calibration(data)
        return data

    def apply_calibration(self, data: CalibrationData) -> None:
        self._calibration_data = data

    def get_calibration_data(self) -> CalibrationData | None:
        return self._calibration_data
