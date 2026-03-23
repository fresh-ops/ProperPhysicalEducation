from typing import Protocol
from ppe_client.domain import SensorDescriptor


class SensorRepository(Protocol):
    async def get_connected_sensors(self) -> list[SensorDescriptor]:
        """Return list of currently connected sensors."""
        ...

    async def get_sensor_state(
        self, descriptor: SensorDescriptor
    ) -> dict | None:
        """Return sensor state (connection status, last data, etc.)."""
        ...