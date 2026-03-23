from typing import Protocol
from ppe_client.domain import SensorDescriptor

class SensorEnumerator(Protocol):
    async def discover(
        self, timeout_s: float = 2.0
    ) -> list[SensorDescriptor]:
        """Scan BLE and return discovered sensors."""
        ...