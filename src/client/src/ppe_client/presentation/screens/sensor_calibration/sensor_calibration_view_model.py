import asyncio
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.sensors import SensorService
from ppe_client.application.sensors.ports import CalibrationData, Sensor

from ...routing.core import ViewModel
from ..sensor_connection import SensorConnectionPayload
from .sensor_calibration_payload import SensorCalibrationPayload


@injectable
class SensorCalibrationViewModel(ViewModel[SensorCalibrationPayload]):
    stage_changed = QtCore.Signal(str)
    progress_changed = QtCore.Signal(int)
    calibration_complete = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    _sensor_service: SensorService
    _sensor: Sensor | None
    _calibration_task: asyncio.Task[None] | None
    _is_calibrating: bool

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._sensor = None
        self._calibration_task = None
        self._is_calibrating = False

    @override
    async def on_enter(self, payload: SensorCalibrationPayload | None = None) -> None:
        if payload is None:
            self.error_occurred.emit("No sensor descriptor provided")
            return

        self._sensor = await self._sensor_service.get_sensor(payload.descriptor)

    @QtCore.Slot()
    def on_start_calibration_clicked(self) -> None:
        if self._is_calibrating or self._sensor is None:
            return

        loop = asyncio.get_running_loop()
        self._calibration_task = loop.create_task(self._perform_calibration())

    async def _perform_calibration(self) -> None:
        self._is_calibrating = True

        if self._sensor is None:
            self.error_occurred.emit("Sensor is not available")
            self._is_calibrating = False
            return

        try:
            self.stage_changed.emit("relaxed")
            relaxed_data = await self._collect_data_with_progress(self._sensor, 5.0)
            print(f"Relaxed data points collected: {len(relaxed_data)}")

            self.stage_changed.emit("tensed")
            tensed_data = await self._collect_data_with_progress(self._sensor, 5.0)
            print(f"Tensed data points collected: {len(tensed_data)}")

            calibration_data = CalibrationData(relaxed_data, tensed_data)
            calibrator = self._sensor_service.get_calibrator()
            calibrator.calculate_thresholds(calibration_data)

            print(
                f"Thresholds calculated: "
                f"low={calibration_data.low_threshold:.2f}, "
                f"mid={calibration_data.mid_threshold:.2f}, "
                f"high={calibration_data.high_threshold:.2f}"
            )

            self._sensor.apply_calibration(calibration_data)

            self.calibration_complete.emit()
            payload = SensorConnectionPayload(descriptor=self._sensor.descriptor())
            self.request_navigation("sensor_connection", payload)

        except Exception as e:
            print(f"Error during calibration: {e}")
            self.error_occurred.emit(f"Calibration failed: {e!s}")
        finally:
            self._is_calibrating = False

    async def _collect_data_with_progress(
        self, sensor: Sensor, duration_s: float
    ) -> list[float]:
        """Collects data in parallel with progress display"""
        values: list[float] = []

        start_time = asyncio.get_running_loop().time()
        end_time = start_time + duration_s

        while asyncio.get_running_loop().time() < end_time:
            values.append(await sensor.read())
            elapsed = asyncio.get_running_loop().time() - start_time
            progress = int((elapsed / duration_s) * 100)
            self.progress_changed.emit(min(progress, 100))
            await asyncio.sleep(0.01)

        self.progress_changed.emit(100)

        return values
