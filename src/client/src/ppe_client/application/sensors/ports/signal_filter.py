from typing import Protocol


class SignalFilter(Protocol):
    """Port: контракт для фильтрации сигнала датчика"""

    def filter(self, raw_value: float) -> float:
        """Фильтрует сырое значение сигнала"""
        ...

    def reset(self) -> None:
        """Сбрасывает состояние фильтра"""
        ...
