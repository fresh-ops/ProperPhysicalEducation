from typing import override

from PySide6 import QtCore
from qasync import asyncSlot
from wireup import injectable

from ppe_client.application.sensors import SensorReader, SensorService
from ppe_client.application.sensors.ports import Sensor
from ppe_client.application.sensors.sensor_value import SensorValue
from ppe_client.domain import SensorDescriptor

from ...routing import Routes
from ...routing.core import ViewModel
from ...stores import SensorStore
from ..sensor_calibration import SensorCalibrationPayload
from ..sensor_discovery import SensorDiscoveryPayload
from .sensor_connection_payload import SensorConnectionPayload


@injectable
class SensorConnectionViewModel(ViewModel[SensorConnectionPayload]):
    connection_error = QtCore.Signal()
    connection_established = QtCore.Signal()
    data_recieved = QtCore.Signal(float)
    calibration_updated = QtCore.Signal(object)

    _sensor_service: SensorService
    _sensor_store: SensorStore
    _sensor: Sensor | None
    _reader: SensorReader | None

    def __init__(
        self, sensor_service: SensorService, sensor_store: SensorStore
    ) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._sensor_store = sensor_store
        self._sensor = None
        self._reader = None

    @override
    async def on_enter(self, payload: SensorConnectionPayload | None = None) -> None:
        if payload is None:
            self.connection_error.emit()
            return

        await self._connect(payload.descriptor)
        if self._sensor is not None and self._sensor.calibration_data is not None:
            self.calibration_updated.emit(self._sensor.calibration_data)

    @asyncSlot()  # type: ignore
    async def on_disconnect_button_clicked(self) -> None:
        self.request_navigation(Routes.SENSOR_DISCOVERY, SensorDiscoveryPayload())
        await self._disconnect()

    @asyncSlot()  # type: ignore
    async def on_exit_button_clicked(self) -> None:
        self.request_navigation(Routes.SENSOR_DISCOVERY, SensorDiscoveryPayload())
        await self._disconnect()

    @asyncSlot()  # type: ignore
    async def on_calibrate_button_clicked(self) -> None:
        if self._sensor is None:
            return
        self.request_navigation(
            Routes.SENSOR_CALIBRATION, SensorCalibrationPayload(self._sensor.descriptor)
        )
        await self._disconnect()

    @asyncSlot()  # type: ignore
    async def on_add_sensor_button_clicked(self) -> None:
        if self._sensor is None:
            return
        self.request_navigation(Routes.SENSOR_DISCOVERY, SensorDiscoveryPayload())
        await self._sensor_store.add(self._sensor.descriptor)
        await self._disconnect()

    async def _connect(self, descriptor: SensorDescriptor) -> None:
        self._sensor = await self._sensor_service.get_sensor(descriptor=descriptor)

        try:
            await self._sensor.connect()
            self.connection_established.emit()
            self._reader = SensorReader(
                self._sensor, self._on_data_recieved, self._on_reading_error
            )
            await self._reader.start()
        except Exception:
            self.connection_error.emit()

    async def _disconnect(self) -> None:
        if self._reader is not None:
            await self._reader.stop()
        if self._sensor is not None:
            await self._sensor.disconnect()

    def _on_data_recieved(self, value: SensorValue) -> None:
        self.data_recieved.emit(value.data)

    def _on_reading_error(self, e: Exception) -> None:
        self.connection_error.emit()
