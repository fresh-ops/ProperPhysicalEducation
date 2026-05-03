import asyncio

from wireup import injectable

from ppe_client.domain.sensor_descriptor import SensorDescriptor


@injectable
class SensorStore:
    _lock: asyncio.Lock
    _sensors: list[SensorDescriptor]

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._sensors = []

    async def get_all(self) -> list[SensorDescriptor]:
        async with self._lock:
            return list.copy(self._sensors)

    async def add(self, sensor: SensorDescriptor) -> None:
        async with self._lock:
            self._sensors.append(sensor)

    async def remove(self, sensor: SensorDescriptor) -> None:
        async with self._lock:
            self._sensors.remove(sensor)
