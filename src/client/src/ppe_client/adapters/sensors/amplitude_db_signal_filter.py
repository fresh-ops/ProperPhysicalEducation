import math


class AmplitudeDbSignalFilter:
    """Transforms each sample into decibels: 20 * log10(abs(x) + EPS)"""

    def __init__(self, eps: float = 1e-8):
        self.eps = eps
        self.last_value: float = 0.0

    def filter(self, value: float) -> float:
        self.last_value = 20 * math.log10(abs(value) + self.eps)
        return self.last_value

    def reset(self) -> None:
        self.last_value = 0.0
