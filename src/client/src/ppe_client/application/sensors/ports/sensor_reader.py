from typing import Protocol


class SensorReader(Protocol):
    """Protocol for reading sensor data."""

    async def read(self) -> float:
        """Read one sensor value."""
        ...
