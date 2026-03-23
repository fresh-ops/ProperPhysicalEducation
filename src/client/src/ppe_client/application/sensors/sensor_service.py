from ppe_client.application.sensors.ports import SensorConnector, SensorEnumerator
from ppe_client.domain import SensorDescriptor


class SensorService:
    def __init__(
        self,
        enumerator: SensorEnumerator,
        connector: SensorConnector,
    ) -> None:
        self._enumerator = enumerator
        self._connector = connector
        self._connected_sensors: dict[str, SensorDescriptor] = {}

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        return await self._enumerator.discover(timeout_s)

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        if await self._connector.connect(descriptor):
            self._connected_sensors[descriptor.identity] = descriptor
            return True
        return False

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        await self._connector.disconnect(descriptor)
        self._connected_sensors.pop(descriptor.identity, None)

    async def disconnect_all(self) -> None:
        for desc in list(self._connected_sensors.values()):
            await self.disconnect(desc)

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        return self._connector.is_connected(descriptor)

    def get_connected_sensors(self) -> list[SensorDescriptor]:
        return list(self._connected_sensors.values())

    async def cleanup(self) -> None:
        await self.disconnect_all()
        if hasattr(self._connector, "cleanup"):
            await self._connector.cleanup()