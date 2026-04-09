from typing import Protocol

from ppe_client.domain import SensorDescriptor

from .sensor_session import SensorSession


class SensorConnector(Protocol):
    """Protocol for connecting to sensors."""

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        """Connect to a sensor."""
        ...

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        """Disconnect from a sensor."""
        ...

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        """Check if sensor is connected."""
        ...

    def get_session(self, descriptor: SensorDescriptor) -> SensorSession | None:
        """Get session for connected sensor."""
        ...

    async def cleanup(self) -> None:
        """Cleanup all connections."""
        ...
