from typing import Protocol

from ppe_client.domain import SensorDescriptor


class SensorConnector(Protocol):
    async def connect(self, descriptor: SensorDescriptor) -> bool:
        """Connect to sensor. Return True if successful."""
        ...

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        """Disconnect from sensor."""
        ...

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        """Check if sensor is currently connected."""
        ...