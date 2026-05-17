from typing import Protocol


class SignalFilter(Protocol):
    """Port: a contract for filtering the sensor signal"""

    def filter(self, raw_value: float) -> float:
        """Filters the raw signal value"""
        ...

    def reset(self) -> None:
        """Resets the filter status"""
        ...
