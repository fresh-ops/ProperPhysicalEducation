from typing import Protocol

from ppe_client.domain import SensorDescriptor

from .sensor import Sensor


class SensorRegistry(Protocol):
    """A sensor registry protocol"""

    async def enumerate(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        """Enumerate available sensors

        Args:
            timeout_s(float): the discovery duration

        Returns:
            list[SensorDescriptor]: the list of available sensors
        """
        ...

    async def get(self, descriptor: SensorDescriptor) -> Sensor:
        """Get a sensor by descriptor

        Returns:
            Sensor: the sensor associated with the specified descriptor
        """
        ...
