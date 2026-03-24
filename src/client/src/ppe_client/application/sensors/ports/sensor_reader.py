from typing import Protocol


class SensorReader(Protocol):
    """Протокол для чтения данных с датчика."""
    
    async def read(self) -> float:
        """Read one value from sensor."""
        ...