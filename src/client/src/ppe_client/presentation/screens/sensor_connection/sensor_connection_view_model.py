import asyncio
from collections import deque
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.sensors import SensorService
from ppe_client.application.sensors.ports import CalibrationData, Sensor
from ppe_client.domain import SensorDescriptor

from ...routing.core import ViewModel
from .sensor_connection_payload import SensorConnectionPayload


@injectable
class SensorConnectionViewModel(ViewModel[SensorConnectionPayload]):
    data_received = QtCore.Signal(float)
    connection_status_changed = QtCore.Signal(str)
    calibration_updated = QtCore.Signal()

    MAX_DATA_POINTS = 500

    _sensor_service: SensorService
    _descriptor: SensorDescriptor | None
    _data_buffer: deque[float]
    _reader_task: asyncio.Task[None] | None

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._descriptor = None
        self._data_buffer = deque(maxlen=self.MAX_DATA_POINTS)
        self._reader_task = None

    @override
    async def on_enter(self, payload: SensorConnectionPayload | None = None) -> None:
        if payload is None:
            self.connection_status_changed.emit("error")
            return

        self._descriptor = payload.descriptor
        await self._connect()

    async def _connect(self) -> None:
        if self._descriptor is None:
            return

        try:
            success = await self._sensor_service.connect(self._descriptor)
            if success:
                self.connection_status_changed.emit("connected")
                self._start_reader_loop()
            else:
                self.connection_status_changed.emit("error")
        except Exception:
            self.connection_status_changed.emit("error")

    def _start_reader_loop(self) -> None:
        if self._descriptor is None or (
            self._reader_task is not None and not self._reader_task.done()
        ):
            return

        sensor = self._sensor_service.get_sensor(self._descriptor)
        if sensor is None:
            return

        self._reader_task = asyncio.get_running_loop().create_task(
            self._read_loop(sensor)
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

    def get_zone(self, value: float) -> str:
        if self._descriptor is None:
            return "unknown"
        return self._sensor_service.get_zone(self._descriptor, value)

    def get_calibration_data(self) -> CalibrationData | None:
        if self._descriptor is None:
            return None
        return self._sensor_service.get_calibration_data(self._descriptor)

    def notify_calibration_updated(self) -> None:
        self.calibration_updated.emit()

    async def disconnect_sensor(self) -> None:
        if self._descriptor is None:
            return

        if self._reader_task is not None:
            self._reader_task.cancel()
            self._reader_task = None

        await self._sensor_service.disconnect(self._descriptor)
        self.connection_status_changed.emit("disconnected")
