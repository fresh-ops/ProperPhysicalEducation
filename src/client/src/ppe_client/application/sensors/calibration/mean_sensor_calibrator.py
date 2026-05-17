from .calibration_data import (
    CalibrationData,
)


class MeanSensorCalibrator:
    def calibrate(
        self, tensed_data: list[float], relaxed_data: list[float]
    ) -> CalibrationData:
        relaxed_avg = sum(relaxed_data) / len(relaxed_data)
        tensed_avg = sum(tensed_data) / len(tensed_data)

        min_val = min(relaxed_avg, tensed_avg)
        max_val = max(relaxed_avg, tensed_avg)
        range_size = max_val - min_val

        low_threshold = min_val + range_size * 0.15
        mid_threshold = min_val + range_size * 0.85
        high_threshold = max_val

        return CalibrationData(
            low_threshold=low_threshold,
            mid_threshold=mid_threshold,
            high_threshold=high_threshold,
        )
