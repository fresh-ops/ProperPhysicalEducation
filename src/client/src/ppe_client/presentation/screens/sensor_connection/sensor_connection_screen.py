import asyncio
from typing import Any, override

from pyqtgraph import PlotWidget
from PySide6 import QtCore, QtWidgets

from ppe_client.presentation.screens.sensor_discovery import SensorDiscoveryPayload

from ...routing.core import Screen
from .sensor_connection_view_model import SensorConnectionViewModel


class SensorConnectionScreen(Screen[SensorConnectionViewModel]):
    _task: asyncio.Task[Any] | None = None

    @override
    def on_create(self) -> None:
        self._title_label = QtWidgets.QLabel("Connected to Sensor")
        self._title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #333;"
        )

        self._plot_widget = PlotWidget()
        self._plot_widget.setLabel("left", "Value")
        self._plot_widget.setLabel("bottom", "Time")
        self._plot_widget.setTitle("EMG Sensor Data")
        self._plot_widget.setBackground("w")
        self._plot_widget.addLegend()
        self._plot_curve = self._plot_widget.plot(
            pen="b", name="EMG Signal", symbolBrush="b", symbolSize=5
        )

        self._status_label = QtWidgets.QLabel("Connecting...")
        self._status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._status_label.setStyleSheet("color: #1976d2; font-weight: bold;")

        self._current_value_label = QtWidgets.QLabel("Current value: --")
        self._current_value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._current_value_label.setStyleSheet("font-size: 14px; color: #555;")

        self._buttons_container = QtWidgets.QHBoxLayout()

        self._disconnect_button = QtWidgets.QPushButton("Disconnect")
        self._disconnect_button.clicked.connect(self._on_disconnect_clicked)
        self._buttons_container.addWidget(self._disconnect_button)

        self._exit_button = QtWidgets.QPushButton("Exit to Sensors List")
        self._exit_button.clicked.connect(self._on_exit_clicked)
        self._exit_button.setVisible(False)
        self._buttons_container.addWidget(self._exit_button)

        self._view_model.data_received.connect(self._on_data_received)
        self._view_model.connection_status_changed.connect(self._on_status_changed)

        root = QtWidgets.QVBoxLayout()
        root.addWidget(self._title_label)
        root.addWidget(self._status_label)
        root.addWidget(self._plot_widget)
        root.addWidget(self._current_value_label)
        root.addLayout(self._buttons_container)

        self.setLayout(root)

    @override
    def on_destroy(self) -> None:
        self._view_model.data_received.disconnect(self._on_data_received)
        self._view_model.connection_status_changed.disconnect(
            self._on_status_changed
        )

    @QtCore.Slot(float)
    def _on_data_received(self, value: float) -> None:
        data_buffer = self._view_model.get_data_buffer()
        x_data = list(range(len(data_buffer)))
        y_data = list(data_buffer)

        self._plot_curve.setData(x_data, y_data)
        self._current_value_label.setText(f"Current value: {value:.4f}")

    @QtCore.Slot(str)
    def _on_status_changed(self, status: str) -> None:
        if status == "connected":
            self._status_label.setText("✓ Connected")
            self._status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            self._disconnect_button.setVisible(True)
            self._exit_button.setVisible(False)
        elif status == "disconnected":
            self._status_label.setText("✗ Disconnected")
            self._status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self._disconnect_button.setVisible(False)
            self._exit_button.setVisible(True)
        else:
            self._status_label.setText("✗ Connection Error")
            self._status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self._disconnect_button.setVisible(False)
            self._exit_button.setVisible(True)

    @QtCore.Slot()
    def _on_disconnect_clicked(self) -> None:
        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._disconnect_and_navigate())

    @QtCore.Slot()
    def _on_exit_clicked(self) -> None:
        self._view_model.request_navigation(
            "sensor_discovery", SensorDiscoveryPayload()
        )

    async def _disconnect_and_navigate(self) -> None:
        await self._view_model.disconnect_sensor()
        self._view_model.request_navigation(
            "sensor_discovery", SensorDiscoveryPayload()
        )