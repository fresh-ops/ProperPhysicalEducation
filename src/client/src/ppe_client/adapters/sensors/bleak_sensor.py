import asyncio
import struct

from bleak import BleakClient

from ppe_client.application.sensors.ports import (
    CalibrationData,
    ValueZone,
)
from ppe_client.domain import SensorDescriptor


class BleakSensor:
    """An adapter for the BleakClient"""

    _CHARACTERISTIC_UUID = "0000503f-0000-1000-8000-00805f9b34fb"

    _client: BleakClient
    _descriptor: SensorDescriptor
    _connections_count: int
    _calibration_data: CalibrationData | None
    _lock: asyncio.Lock

    def __init__(
        self,
        descriptor: SensorDescriptor,
    ) -> None:
        self._client = BleakClient(descriptor.address)
        self._descriptor = descriptor
        self._connections_count = 0
        self._calibration_data = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._lock:
            if self._connections_count == 0:
                await self._client.connect()
            self._connections_count += 1

    async def disconnect(self) -> None:
        async with self._lock:
            if self._connections_count == 0:
                return
            self._connections_count -= 1
            if self._connections_count == 0:
                await self._client.disconnect()

    @property
    def descriptor(self) -> SensorDescriptor:
        return self._descriptor

    def is_connected(self) -> bool:
        return self._connections_count > 0

    async def read(self) -> float:
        async with self._lock:
            raw_data = await self._client.read_gatt_char(self._CHARACTERISTIC_UUID)
        return float(struct.unpack("f", raw_data)[0])

    async def read_with_zone(self) -> tuple[float, ValueZone]:
        value = await self.read()
        if not self._calibration_data:
            return value, ValueZone.UNKNOWN
        return value, self._calibration_data.zone_of(value)

    def apply_calibration(self, data: CalibrationData) -> None:
        self._calibration_data = data

    @property
    def calibration_data(self) -> CalibrationData | None:
        return self._calibration_data
