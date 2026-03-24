from typing import Protocol
from collections.abc import Callable


class SensorSession(Protocol):
    """Протокол для работы с подключённым датчиком."""
    
    def attach(self, callback: Callable[[float], None]) -> None:
        """Attach callback to receive sensor readings."""
        ...

    def detach(self, callback: Callable[[float], None]) -> None:
        """Detach callback from sensor readings."""
        ...

    def terminate(self) -> bool:
        """Terminate this session."""
        ...