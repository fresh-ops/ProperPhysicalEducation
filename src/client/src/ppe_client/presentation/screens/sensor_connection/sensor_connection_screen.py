from collections import deque
from typing import override

from pyqtgraph import LinearRegionItem, PlotWidget
from PySide6 import QtCore, QtGui, QtWidgets

from ppe_client.application.sensors.calibration.calibration_data import CalibrationData

from ...routing.core import Screen
from .sensor_connection_view_model import SensorConnectionViewModel


class SensorConnectionScreen(Screen[SensorConnectionViewModel]):
    _data_buffer: deque[float]
    _calibration: CalibrationData | None

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

        self._add_button = QtWidgets.QPushButton("Add Sensor")
        self._add_button.clicked.connect(self._view_model.on_add_sensor_button_clicked)
        self._add_button.setVisible(False)
        self._buttons_container.addWidget(self._add_button)

        self._disconnect_button = QtWidgets.QPushButton("Disconnect")
        self._disconnect_button.clicked.connect(
            self._view_model.on_disconnect_button_clicked
        )
        self._disconnect_button.setVisible(False)
        self._buttons_container.addWidget(self._disconnect_button)

        self._exit_button = QtWidgets.QPushButton("Exit to Sensors List")
        self._exit_button.clicked.connect(self._view_model.on_exit_button_clicked)
        self._buttons_container.addWidget(self._exit_button)

        root = QtWidgets.QVBoxLayout()
        root.addWidget(self._title_label)
        root.addWidget(self._status_label)
        root.addWidget(self._plot_widget)
        root.addWidget(self._current_value_label)
        root.addLayout(self._buttons_container)

        self.setLayout(root)

        self._data_buffer = deque(maxlen=100)
        self._calibration = None
        self._view_model.connection_error.connect(self._on_connection_error)
        self._view_model.connection_established.connect(self._on_connection_established)
        self._view_model.data_recieved.connect(self._on_data_recieved)
        self._view_model.calibration_updated.connect(self._on_calibration_updated)

    @override
    def on_destroy(self) -> None:
        self._disconnect_button.clicked.disconnect(
            self._view_model.on_disconnect_button_clicked
        )
        self._exit_button.clicked.disconnect(self._view_model.on_exit_button_clicked)
        self._add_button.clicked.disconnect(
            self._view_model.on_add_sensor_button_clicked
        )
        self._calibrate_button.clicked.disconnect(
            self._view_model.on_calibrate_button_clicked
        )

        self._view_model.connection_error.disconnect(self._on_connection_error)
        self._view_model.connection_established.disconnect(
            self._on_connection_established
        )
        self._view_model.data_recieved.disconnect(self._on_data_recieved)
        self._view_model.calibration_updated.disconnect(self._on_calibration_updated)

    @QtCore.Slot()
    def _on_connection_error(self) -> None:
        self._status_label.setText("Connection Error")
        self._status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self._add_button.setVisible(False)
        self._calibrate_button.setVisible(False)
        self._disconnect_button.setVisible(False)
        self._exit_button.setVisible(True)

    @QtCore.Slot()
    def _on_connection_established(self) -> None:
        self._status_label.setText("Connected")
        self._status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        self._add_button.setVisible(self._calibration is not None)
        self._calibrate_button.setVisible(self._calibration is None)
        self._disconnect_button.setVisible(True)
        self._exit_button.setVisible(False)

    @QtCore.Slot(float)
    def _on_data_recieved(self, data: float) -> None:
        self._data_buffer.append(data)
        x_coords = [0.01 * i for i, _ in enumerate(self._data_buffer)]

        self._plot_curve.setData(x_coords, self._data_buffer, pen="k")
        self._current_value_label.setText(f"Current value: {data:.4f}")
        self._update_zones()

    @QtCore.Slot(object)
    def _on_calibration_updated(self, calibration: CalibrationData) -> None:
        self._calibration = calibration
        self._add_button.setVisible(True)
        self._calibrate_button.setVisible(False)

    def _update_zones(self) -> None:
        if self._calibration is None:
            return
        for item in list(self._plot_widget.items()):
            if isinstance(item, LinearRegionItem):
                self._plot_widget.removeItem(item)

        max_displayed = max(self._data_buffer)
        min_displayed = min(self._data_buffer)

        red_end = max(max_displayed, self._calibration.high_threshold)

        green_region = LinearRegionItem(
            [min_displayed, self._calibration.low_threshold],
            orientation="horizontal",
            movable=False,
        )
        green_region.setBrush(QtGui.QColor(0, 255, 0, 50))
        green_region.setZValue(-1)
        self._plot_widget.addItem(green_region)

        yellow_region = LinearRegionItem(
            [self._calibration.low_threshold, self._calibration.mid_threshold],
            orientation="horizontal",
            movable=False,
        )
        yellow_region.setBrush(QtGui.QColor(255, 255, 0, 50))
        yellow_region.setZValue(-1)
        self._plot_widget.addItem(yellow_region)

        red_region = LinearRegionItem(
            [self._calibration.mid_threshold, red_end],
            orientation="horizontal",
            movable=False,
        )
        red_region.setBrush(QtGui.QColor(255, 0, 0, 50))
        red_region.setZValue(-1)
        self._plot_widget.addItem(red_region)
