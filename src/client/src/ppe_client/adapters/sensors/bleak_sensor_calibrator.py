import asyncio
from typing import Any

from wireup import injectable

from ppe_client.application.sensors.ports import (
    CalibrationData,
    SensorCalibrator,
    SensorSession,
)


@injectable(as_type=SensorCalibrator)
class BleakSensorCalibrator:
    async def calibrate(
        self, session: SensorSession, duration_s: float = 5.0
    ) -> CalibrationData:
        relaxed_values = await self._collect_data(session, duration_s)
        tensed_values = await self._collect_data(session, duration_s)

        data = CalibrationData(relaxed_values, tensed_values)
        self.calculate_thresholds(data)
        return data

    async def _collect_data(self, session: Any, duration_s: float) -> list[float]:
        values: list[float] = []

        def on_data(value: float) -> None:
            values.append(value)

        session.attach(on_data)
        await asyncio.sleep(duration_s)
        session.detach(on_data)

        return values

    def calculate_thresholds(self, data: CalibrationData) -> None:
        if not data.relaxed_values or not data.tensed_values:
            return

        relaxed_avg = sum(data.relaxed_values) / len(data.relaxed_values)
        tensed_avg = sum(data.tensed_values) / len(data.tensed_values)

        min_val = min(relaxed_avg, tensed_avg)
        max_val = max(relaxed_avg, tensed_avg)
        range_size = max_val - min_val

        data.low_threshold = min_val + range_size * 0.15

        data.mid_threshold = min_val + range_size * 0.85

        data.high_threshold = max_val

    def get_zone(self, value: float, data: CalibrationData) -> str:
        if value < data.low_threshold:
            return "green"
        elif value < data.mid_threshold:
            return "yellow"
        else:
            return "red"
