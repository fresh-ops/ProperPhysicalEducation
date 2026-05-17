import asyncio
import struct
import time

from bleak import BleakClient

from ppe_client.application.sensors.calibration import (
    CalibrationData,
    ValueZone,
)
from ppe_client.application.sensors.sensor_value import SensorValue
from ppe_client.domain import SensorDescriptor

from .ema_signal_filter import EMASignalFilter


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
        self._signal_filter = EMASignalFilter()

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

    async def read(self) -> SensorValue:
        async with self._lock:
            raw_data = await self._client.read_gatt_char(self._CHARACTERISTIC_UUID)
        data = float(struct.unpack("f", raw_data)[0])
        filtered_data = self._signal_filter.filter(data)
        zone = ValueZone.UNKNOWN
        if self._calibration_data is not None:
            zone = self._calibration_data.zone_of(data)
        timestamp_ms = time.time_ns() // 1_000_000
        return SensorValue(data=filtered_data, zone=zone, timestamp_ms=timestamp_ms)

    def apply_calibration(self, data: CalibrationData) -> None:
        self._calibration_data = data

    @property
    def calibration_data(self) -> CalibrationData | None:
        return self._calibration_data
