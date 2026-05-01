from dataclasses import dataclass


@dataclass()
class CalibrationData:
    relaxed_values: list[float]
    tensed_values: list[float]
    low_threshold: float = 0.0
    mid_threshold: float = 0.0
    high_threshold: float = 0.0
