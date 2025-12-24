class EMGFilter:
    def __init__(self):
        self.filter_coefficient = 0.3
        self.previous_raw_value = 0.0
        self.previous_filtered_value = 0.0
        self.filtered_value = 0.0

    """
    Фильтрует EMG сигнал с помощью EMA

    Args:
        raw_value: сырое значение EMG сигнала
    
    Returns:
        Отфильтрованное значение
    """
    def filter(self, raw_value: float) -> float:
        self.previous_filtered_value = self.filtered_value

        self.filtered_value = abs(self.previous_raw_value - raw_value) * \
            self.filter_coefficient + self.filtered_value * (1.0 - self.filter_coefficient)
        self.previous_raw_value = raw_value
        return self.filtered_value
