from collections.abc import Callable
from typing import Protocol


class SensorSession(Protocol):
    """Protocol for working with connected sensor."""

    def attach(self, callback: Callable[[float], None]) -> None:
        """Attach callback for sensor data."""
        ...

    def detach(self, callback: Callable[[float], None]) -> None:
        """Detach callback from sensor data."""
        ...

    def terminate(self) -> bool:
        """Terminate the session."""
        ...
