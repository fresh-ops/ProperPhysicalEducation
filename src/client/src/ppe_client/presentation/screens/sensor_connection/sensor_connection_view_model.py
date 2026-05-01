import asyncio
from collections import deque
from typing import override

from PySide6 import QtCore
from qasync import asyncSlot
from wireup import injectable

from ppe_client.application.sensors import SensorService
from ppe_client.application.sensors.calibration import CalibrationData
from ppe_client.application.sensors.ports import Sensor
from ppe_client.domain import SensorDescriptor
from ppe_client.presentation.screens.sensor_calibration import (
    SensorCalibrationPayload,
)
from ppe_client.presentation.screens.sensor_discovery import (
    SensorDiscoveryPayload,
)

from ...routing.core import ViewModel
from .sensor_connection_payload import SensorConnectionPayload


@injectable
class SensorConnectionViewModel(ViewModel[SensorConnectionPayload]):
    data_received = QtCore.Signal(float)
    connection_status_changed = QtCore.Signal(str)
    calibration_updated = QtCore.Signal()

    MAX_DATA_POINTS = 500

    _sensor_service: SensorService
    _sensor: Sensor | None
    _data_buffer: deque[float]
    _reader_task: asyncio.Task[None] | None

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._sensor = None
        self._data_buffer = deque(maxlen=self.MAX_DATA_POINTS)
        self._reader_task = None

    @override
    async def on_enter(self, payload: SensorConnectionPayload | None = None) -> None:
        if payload is None:
            self.connection_status_changed.emit("error")
            return

        await self._connect(payload.descriptor)

    async def _connect(self, descriptor: SensorDescriptor) -> None:
        if descriptor is None:
            return

        self._sensor = await self._sensor_service.get_sensor(descriptor)
        try:
            await self._sensor.connect()
            if self._sensor.is_connected():
                self.connection_status_changed.emit("connected")
                await self._start_reader_loop()
            else:
                self.connection_status_changed.emit("error")
        except Exception:
            self.connection_status_changed.emit("error")

    async def _start_reader_loop(self) -> None:
        if self._sensor is None or (
            self._reader_task is not None and not self._reader_task.done()
        ):
            return

        self._reader_task = asyncio.get_running_loop().create_task(
            self._read_loop(self._sensor)
        )

    async def _read_loop(self, sensor: Sensor) -> None:
        try:
            while True:
                self._on_sensor_data(await sensor.read())
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            return
        except Exception:
            self.connection_status_changed.emit("error")

    def _on_sensor_data(self, value: float) -> None:
        self._data_buffer.append(value)
        self.data_received.emit(value)

    def get_data_buffer(self) -> deque[float]:
        return self._data_buffer

    def get_calibration_data(self) -> CalibrationData | None:
        if self._sensor is None:
            return None
        return self._sensor.calibration_data

    def notify_calibration_updated(self) -> None:
        self.calibration_updated.emit()

    def get_descriptor(self) -> SensorDescriptor | None:
        if self._sensor is None:
            return None
        return self._sensor.descriptor

    async def disconnect_sensor(self) -> None:
        if self._sensor is None:
            return

        if self._reader_task is not None:
            self._reader_task.cancel()
            self._reader_task = None

        await self._sensor.disconnect()
        self.connection_status_changed.emit("disconnected")

    @asyncSlot()  # type: ignore
    async def on_calibrate_button_clicked(self) -> None:
        if self._sensor is None:
            return
        payload = SensorCalibrationPayload(descriptor=self._sensor.descriptor)
        self.request_navigation("sensor_calibration", payload)
        await self.disconnect_sensor()

    @asyncSlot()  # type: ignore
    async def on_exit_button_clicked(self) -> None:
        self.request_navigation("sensor_discovery", SensorDiscoveryPayload())
        await self.disconnect_sensor()
