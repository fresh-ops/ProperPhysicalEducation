from typing import override
from wireup import injectable

from ppe_client.adapters.sensors.bleak_sensor_connector import BleakSensorConnector
from ppe_client.adapters.sensors.bleak_sensor_enumerator import BleakSensorEnumerator
from ppe_client.domain import SensorDescriptor

from .ports.sensor_repository import SensorRepository
from ppe_client.application.sensors.ports import SensorSession


@injectable
class SensorService:
    """Service for managing sensor discovery and connection."""

    def __init__(
        self, enumerator: BleakSensorEnumerator, connector: BleakSensorConnector
    ) -> None:
        self._enumerator = enumerator
        self._connector = connector
        self._repository: SensorRepository = SensorRepository()

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        """Discover available sensors."""
        return await self._enumerator.discover(timeout_s)

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        """Connect to a sensor."""
        success = await self._connector.connect(descriptor)
        if success:
            self._repository.add(descriptor)
        return success

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        """Disconnect from a sensor."""
        await self._connector.disconnect(descriptor)
        self._repository.remove(descriptor)

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        """Check if sensor is connected."""
        return self._connector.is_connected(descriptor)

    def get_session(self, descriptor: SensorDescriptor) -> SensorSession | None:
        """Get session for connected sensor."""
        return self._connector.get_session(descriptor)

    def get_all_connected(self) -> list[SensorDescriptor]:
        """Get all connected sensors."""
        return self._repository.get_all()

    async def cleanup(self) -> None:
        """Cleanup all connections."""
        await self._connector.cleanup()
        self._repository.clear()