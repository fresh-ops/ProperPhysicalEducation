from collections import deque
from collections.abc import Callable
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.domain import SensorDescriptor

from ...routing.core import ViewModel
from .sensor_connection_payload import SensorConnectionPayload


@injectable
class SensorConnectionViewModel(ViewModel[SensorConnectionPayload]):
    data_received = QtCore.Signal(float)
    connection_status_changed = QtCore.Signal(str)

    MAX_DATA_POINTS = 500

    _sensor_service: SensorService
    _descriptor: SensorDescriptor | None
    _data_buffer: deque[float]
    _callback_registered: bool
    _callback: Callable[[float], None] | None

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._descriptor = None
        self._data_buffer = deque(maxlen=self.MAX_DATA_POINTS)
        self._callback_registered = False
        self._callback = None

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
                self._attach_callback()
            else:
                self.connection_status_changed.emit("error")
        except Exception:
            self.connection_status_changed.emit("error")

    def _attach_callback(self) -> None:
        if self._descriptor is None:
            return
        session = self._sensor_service.get_session(self._descriptor)
        if session and not self._callback_registered:

            def on_data(value: float) -> None:
                self._on_sensor_data(value)

            session.attach(on_data)
            self._callback = on_data
            self._callback_registered = True

    def _on_sensor_data(self, value: float) -> None:
        self._data_buffer.append(value)
        self.data_received.emit(value)

    def get_data_buffer(self) -> deque[float]:
        return self._data_buffer

    async def disconnect_sensor(self) -> None:
        if self._descriptor is None:
            return

        session = self._sensor_service.get_session(self._descriptor)
        if session and self._callback_registered and self._callback is not None:
            session.detach(self._callback)
            self._callback_registered = False

        await self._sensor_service.disconnect(self._descriptor)
        self.connection_status_changed.emit("disconnected")
