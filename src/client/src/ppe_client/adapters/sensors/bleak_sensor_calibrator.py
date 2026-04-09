import asyncio
from typing import TYPE_CHECKING, Any

from ppe_client.application.sensors.ports.sensor_calibrator import (
    CalibrationData,
    SensorCalibrator,
)
from ppe_client.domain import SensorDescriptor

if TYPE_CHECKING:
    from ppe_client.application.sensors.sensor_service import SensorService


class BleakSensorCalibrator(SensorCalibrator):
    def __init__(self, sensor_service: "SensorService") -> None:
        self._sensor_service = sensor_service

    async def calibrate(
        self, descriptor: SensorDescriptor, duration_s: float = 5.0
    ) -> CalibrationData:
        session = self._sensor_service.get_session(descriptor)
        if not session:
            raise ValueError("Sensor not connected")

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

        data.low_threshold = relaxed_avg * 1.2
        data.mid_threshold = (relaxed_avg + tensed_avg) / 2
        data.high_threshold = tensed_avg * 0.8

    def get_zone(self, value: float, data: CalibrationData) -> str:
        if value < data.low_threshold:
            return "green"
        elif value < data.mid_threshold:
            return "yellow"
        else:
            return "red"
