import asyncio

from bleak import BleakScanner
from wireup import injectable

from ppe_client.application.sensors.ports import (
    Sensor,
    SensorCalibrator,
    SensorRegistry,
)
from ppe_client.domain import SensorDescriptor

from .bleak_sensor import BleakSensor


@injectable(as_type=SensorRegistry)
class BleakSensorRegistry:
    _DEVICE_UUID = "0000503e-0000-1000-8000-00805f9b34fb"
    _TARGET_NAME = "PPE Sensor"

    _sensors: dict[str, Sensor]
    _lock: asyncio.Lock

    def __init__(self, calibrator: SensorCalibrator | None = None) -> None:
        self._sensors = {}
        self._lock = asyncio.Lock()
        self._calibrator = calibrator

    async def enumerate(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        devices = await BleakScanner.discover(timeout=timeout_s)

        result: list[SensorDescriptor] = []
        seen_addresses: set[str] = set()

        for dev in devices:
            name = getattr(dev, "name", None)
            if name is None or name != self._TARGET_NAME:
                continue

            address = getattr(dev, "address", None)
            if address is None:
                continue

            if address in seen_addresses:
                continue

            seen_addresses.add(address)
            result.append(SensorDescriptor(name=name, address=address))

        return result

    async def get(self, descriptor: SensorDescriptor) -> Sensor:
        async with self._lock:
            if descriptor.identity not in self._sensors:
                self._sensors[descriptor.identity] = BleakSensor(
                    descriptor, calibrator=self._calibrator
                )
            return self._sensors[descriptor.identity]
