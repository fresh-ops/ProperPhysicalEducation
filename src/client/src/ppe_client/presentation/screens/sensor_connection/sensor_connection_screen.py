import asyncio
from typing import Any, override

from pyqtgraph import LinearRegionItem, PlotWidget
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QColor

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
        self._plot_widget.setLabel("left", "EMG Signal (μV)")
        self._plot_widget.setTitle("EMG Sensor Data")
        self._plot_widget.setBackground("w")
        self._plot_widget.addLegend()
        self._plot_widget.getAxis("bottom").setStyle(showValues=False)
        self._plot_curve = self._plot_widget.plot(
            pen="k", name="EMG Signal", symbolBrush="k", symbolSize=5
        )

        self._status_label = QtWidgets.QLabel("Connecting...")
        self._status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._status_label.setStyleSheet("color: #1976d2; font-weight: bold;")

        self._current_value_label = QtWidgets.QLabel("Current value: --")
        self._current_value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._current_value_label.setStyleSheet("font-size: 14px; color: #555;")

        self._buttons_container = QtWidgets.QHBoxLayout()

        self._calibrate_button = QtWidgets.QPushButton("Calibrate")
        self._calibrate_button.clicked.connect(
            self._view_model.on_calibrate_button_clicked
        )
        self._calibrate_button.setVisible(False)
        self._buttons_container.addWidget(self._calibrate_button)

        self._disconnect_button = QtWidgets.QPushButton("Disconnect")
        self._disconnect_button.clicked.connect(self._view_model.on_exit_button_clicked)
        self._buttons_container.addWidget(self._disconnect_button)

        self._exit_button = QtWidgets.QPushButton("Exit to Sensors List")
        self._exit_button.clicked.connect(self._view_model.on_exit_button_clicked)
        self._exit_button.setVisible(False)
        self._buttons_container.addWidget(self._exit_button)

        self._view_model.data_received.connect(self._on_data_received)
        self._view_model.connection_status_changed.connect(self._on_status_changed)
        self._view_model.calibration_updated.connect(self._on_calibration_updated)

        root = QtWidgets.QVBoxLayout()
        root.addWidget(self._title_label)
        root.addWidget(self._status_label)
        root.addWidget(self._plot_widget)
        root.addWidget(self._current_value_label)
        root.addLayout(self._buttons_container)

        self.setLayout(root)

        self._view_model.notify_calibration_updated()

    @override
    def on_destroy(self) -> None:
        self._view_model.data_received.disconnect(self._on_data_received)
        self._view_model.connection_status_changed.disconnect(self._on_status_changed)
        self._view_model.calibration_updated.disconnect(self._on_calibration_updated)

        self._calibrate_button.clicked.disconnect(
            self._view_model.on_calibrate_button_clicked
        )
        self._exit_button.clicked.disconnect(self._view_model.on_exit_button_clicked)
        self._disconnect_button.clicked.connect(self._view_model.on_exit_button_clicked)

    @QtCore.Slot(float)
    def _on_data_received(self, value: float) -> None:
        data_buffer = self._view_model.get_data_buffer()

        window_size = 100
        if len(data_buffer) > window_size:
            displayed_data = list(data_buffer)[-window_size:]
        else:
            displayed_data = list(data_buffer)

        x_data = [i * 0.01 for i in range(len(displayed_data))]
        y_data = displayed_data

        self._plot_curve.setData(x_data, y_data, pen="k")

        if y_data:
            min_val = min(y_data)
            max_val = max(y_data)
            margin = (max_val - min_val) * 0.1 if max_val > min_val else 10
            self._plot_widget.setYRange(min_val - margin, max_val + margin, padding=0)

        calibration_data = self._view_model.get_calibration_data()
        if calibration_data is not None and y_data:
            min_displayed = min(y_data)
            max_displayed = max(y_data)
            self._update_background_zones(
                calibration_data.low_threshold,
                calibration_data.mid_threshold,
                calibration_data.high_threshold,
                min_displayed,
                max_displayed,
            )

        self._current_value_label.setText(f"Current value: {value:.4f}")

    def _update_background_zones(
        self,
        low: float,
        mid: float,
        high: float,
        min_displayed: float,
        max_displayed: float,
    ) -> None:
        for item in list(self._plot_widget.items()):
            if isinstance(item, LinearRegionItem):
                self._plot_widget.removeItem(item)

        if low == 0.0 and mid == 0.0 and high == 0.0:
            return

        display_range = max_displayed - min_displayed
        green_size = display_range * 0.15
        yellow_size = display_range * 0.7
        red_size = display_range * 0.15

        green_start = min_displayed
        green_end = green_start + green_size

        yellow_start = green_end
        yellow_end = yellow_start + yellow_size

        red_start = yellow_end
        red_end = red_start + red_size

        green_region = LinearRegionItem(
            [green_start, green_end], orientation="horizontal", movable=False
        )
        green_region.setBrush(QColor(0, 255, 0, 50))
        green_region.setZValue(-1)
        self._plot_widget.addItem(green_region)

        yellow_region = LinearRegionItem(
            [yellow_start, yellow_end],
            orientation="horizontal",
            movable=False,
        )
        yellow_region.setBrush(QColor(255, 255, 0, 50))
        yellow_region.setZValue(-1)
        self._plot_widget.addItem(yellow_region)

        red_region = LinearRegionItem(
            [red_start, red_end], orientation="horizontal", movable=False
        )
        red_region.setBrush(QColor(255, 0, 0, 50))
        red_region.setZValue(-1)
        self._plot_widget.addItem(red_region)

    @QtCore.Slot()
    def _on_calibration_updated(self) -> None:
        calibration_data = self._view_model.get_calibration_data()
        if calibration_data is not None:
            data_buffer = self._view_model.get_data_buffer()
            if data_buffer:
                min_displayed = min(data_buffer)
                max_displayed = max(data_buffer)
                self._update_background_zones(
                    calibration_data.low_threshold,
                    calibration_data.mid_threshold,
                    calibration_data.high_threshold,
                    min_displayed,
                    max_displayed,
                )

    @QtCore.Slot(str)
    def _on_status_changed(self, status: str) -> None:
        if status == "connected":
            self._status_label.setText("✓ Connected")
            self._status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            self._calibrate_button.setVisible(True)
            self._disconnect_button.setVisible(True)
            self._exit_button.setVisible(False)
        elif status == "disconnected":
            self._status_label.setText("✗ Disconnected")
            self._status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self._calibrate_button.setVisible(False)
            self._disconnect_button.setVisible(False)
            self._exit_button.setVisible(True)
        else:
            self._status_label.setText("✗ Connection Error")
            self._status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self._calibrate_button.setVisible(False)
            self._disconnect_button.setVisible(False)
            self._exit_button.setVisible(True)
