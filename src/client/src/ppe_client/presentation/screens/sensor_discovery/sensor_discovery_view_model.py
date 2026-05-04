import asyncio
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.domain import SensorDescriptor

from ...routing.core import ViewModel
from ..sensor_connection import SensorConnectionPayload
from .sensor_discovery_payload import SensorDiscoveryPayload


@injectable
class SensorDiscoveryViewModel(ViewModel[SensorDiscoveryPayload]):
    sensors_updated = QtCore.Signal(list)
    scanning_changed = QtCore.Signal(bool)
    error_occurred = QtCore.Signal(str)

    _sensor_service: SensorService
    _discovered_sensors: list[SensorDescriptor]
    _is_scanning: bool

    def __init__(self, sensor_service: SensorService) -> None:
        super().__init__()
        self._sensor_service = sensor_service
        self._discovered_sensors = []
        self._is_scanning = False
        self._scan_task: asyncio.Task[None] | None = None

    @override
    async def on_enter(self, payload: SensorDiscoveryPayload | None = None) -> None:
        self.scanning_changed.emit(False)
        self.sensors_updated.emit([])

    @QtCore.Slot()
    def on_scan_clicked(self) -> None:
        if self._is_scanning:
            return

        loop = asyncio.get_running_loop()
        self._scan_task = loop.create_task(self._perform_scan())

    async def _perform_scan(self) -> None:
        self._is_scanning = True
        self.scanning_changed.emit(True)
        self._discovered_sensors = []
        self.error_occurred.emit("")

        try:
            self._discovered_sensors = await self._sensor_service.discover(
                timeout_s=5.0
            )
            if not self._discovered_sensors:
                self.error_occurred.emit(
                    "No sensors required for Proper Physical Education found nearby"
                )
            else:
                display_list = [f"Found {len(self._discovered_sensors)} sensor(s)"] + [
                    f"{s.name} ({s.address})" for s in self._discovered_sensors
                ]
                self.sensors_updated.emit(display_list)
                self.error_occurred.emit("")
        except Exception:
            self.error_occurred.emit(
                "Error scanning for sensors. Make sure Bluetooth is enabled."
            )
        finally:
            self._is_scanning = False
            self.scanning_changed.emit(False)

    @QtCore.Slot(int)
    def on_sensor_selected(self, index: int) -> None:
        """Handle sensor selection from combo box."""
        if index <= 0:
            return
        if (index - 1) < len(self._discovered_sensors):
            selected_sensor = self._discovered_sensors[index - 1]
            payload = SensorConnectionPayload(descriptor=selected_sensor)
            self.request_navigation("sensor_connection", payload)
