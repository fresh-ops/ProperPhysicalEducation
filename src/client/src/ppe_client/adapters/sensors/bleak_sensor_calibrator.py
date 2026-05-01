import asyncio

from wireup import injectable

from ppe_client.application.sensors.ports import (
    CalibrationData,
    Sensor,
    SensorCalibrator,
)


# TODO: separate this class from Bleak
@injectable(as_type=SensorCalibrator)
class BleakSensorCalibrator:
    async def calibrate(
        self, sensor: Sensor, duration_s: float = 5.0
    ) -> CalibrationData:
        relaxed_values = await self._collect_data(sensor, duration_s)
        tensed_values = await self._collect_data(sensor, duration_s)

        data = CalibrationData(relaxed_values, tensed_values)
        self.calculate_thresholds(data)
        return data

    async def _collect_data(self, sensor: Sensor, duration_s: float) -> list[float]:
        values: list[float] = []

        end_time = asyncio.get_running_loop().time() + duration_s
        while asyncio.get_running_loop().time() < end_time:
            values.append(await sensor.read())
            await asyncio.sleep(0.01)

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

    # TODO: move this method to CalibrationData
    def get_zone(self, value: float, data: CalibrationData) -> str:
        if value < data.low_threshold:
            return "green"
        elif value < data.mid_threshold:
            return "yellow"
        else:
            return "red"
