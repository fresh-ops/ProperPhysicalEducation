from ppe_client.application.sensors.ports.signal_filter import SignalFilter

class EMASignalFilter:
    """Экспоненциальное скользящее среднее (EMA) для фильтрации EMG"""
    
    def __init__(self, filter_coefficient: float = 0.3):
        self.filter_coefficient = filter_coefficient
        self.previous_raw_value = 0.0
        self.previous_filtered_value = 0.0
        self.filtered_value = 0.0
    
    def filter(self, raw_value: float) -> float:
        self.previous_filtered_value = self.filtered_value
        self.filtered_value = (
            abs(self.previous_raw_value - raw_value) * self.filter_coefficient +
            self.filtered_value * (1.0 - self.filter_coefficient)
        )
        self.previous_raw_value = raw_value
        return self.filtered_value
    
    def reset(self) -> None:
        self.previous_raw_value = 0.0
        self.previous_filtered_value = 0.0
        self.filtered_value = 0.0