import asyncio
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.domain import SensorDescriptor

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
    _descriptor: SensorDescriptor | None
    _calibration_task: asyncio.Task[None] | None
    _is_calibrating: bool

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._descriptor = None
        self._calibration_task = None
        self._is_calibrating = False

    @override
    async def on_enter(self, payload: SensorCalibrationPayload | None = None) -> None:
        if payload is None:
            self.error_occurred.emit("No sensor descriptor provided")
            return

        self._descriptor = payload.descriptor

    @QtCore.Slot()
    def on_start_calibration_clicked(self) -> None:
        if self._is_calibrating or self._descriptor is None:
            return

        loop = asyncio.get_running_loop()
        self._calibration_task = loop.create_task(self._perform_calibration())

    async def _perform_calibration(self) -> None:
        self._is_calibrating = True

        if self._descriptor is None:
            self.error_occurred.emit("Sensor descriptor is not available")
            self._is_calibrating = False
            return

        try:
            self.stage_changed.emit("relaxed")
            await self._timer_with_progress(5.0)

            self.stage_changed.emit("tensed")
            await self._timer_with_progress(5.0)

            await self._sensor_service.calibrate(self._descriptor, duration_s=5.0)

            self.calibration_complete.emit()

            payload = SensorConnectionPayload(descriptor=self._descriptor)
            self.request_navigation("sensor_connection", payload)

        except Exception as e:
            print(f"Error during calibration: {e}")
            self.error_occurred.emit(f"Calibration failed: {e!s}")
        finally:
            self._is_calibrating = False

    async def _timer_with_progress(self, duration_s: float) -> None:
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + duration_s

        while asyncio.get_event_loop().time() < end_time:
            elapsed = asyncio.get_event_loop().time() - start_time
            progress = int((elapsed / duration_s) * 100)
            self.progress_changed.emit(min(progress, 100))
            await asyncio.sleep(0.1)

        self.progress_changed.emit(100)
