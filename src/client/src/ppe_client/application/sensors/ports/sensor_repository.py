from ppe_client.domain import SensorDescriptor


class SensorRepository:
    """Repository for managing sensor descriptors."""

    def __init__(self) -> None:
        self._sensors: dict[str, SensorDescriptor] = {}

    def add(self, descriptor: SensorDescriptor) -> None:
        """Add a sensor to the repository."""
        self._sensors[descriptor.identity] = descriptor

    def remove(self, descriptor: SensorDescriptor) -> None:
        """Remove a sensor from the repository."""
        self._sensors.pop(descriptor.identity, None)

    def get(self, identity: str) -> SensorDescriptor | None:
        """Get a sensor by identity."""
        return self._sensors.get(identity)

    def get_all(self) -> list[SensorDescriptor]:
        """Get all sensors in the repository."""
        return list(self._sensors.values())

    def clear(self) -> None:
        """Clear all sensors from the repository."""
        self._sensors.clear()
