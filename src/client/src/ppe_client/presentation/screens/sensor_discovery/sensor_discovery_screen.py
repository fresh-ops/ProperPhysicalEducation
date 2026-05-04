from typing import override

from PySide6 import QtCore, QtWidgets

from ...routing.core import Screen
from .sensor_discovery_view_model import SensorDiscoveryViewModel


class SensorDiscoveryScreen(Screen[SensorDiscoveryViewModel]):
    @override
    def on_create(self) -> None:
        self._title_label = QtWidgets.QLabel("Discover Sensors")
        self._title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #333;"
        )

        self._scan_button = QtWidgets.QPushButton("Scan for Sensors")
        self._scan_button.clicked.connect(self._view_model.on_scan_clicked)

        self._sensor_list = QtWidgets.QComboBox()
        self._sensor_list.currentIndexChanged.connect(
            self._view_model.on_sensor_selected
        )

        self._done_button = QtWidgets.QPushButton("Done")
        self._done_button.setStyleSheet("background: #35baf6")
        self._done_button.clicked.connect(self._view_model.on_done_button_clicked)

        self._loading_spinner = QtWidgets.QLabel("Scanning...")
        self._loading_spinner.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._loading_spinner.setStyleSheet("color: #666; font-style: italic;")
        self._loading_spinner.setVisible(False)

        self._error_label = QtWidgets.QLabel()
        self._error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self._error_label.setVisible(False)

        self._view_model.sensors_updated.connect(self.on_sensors_updated)
        self._view_model.scanning_changed.connect(self.on_scanning_changed)
        self._view_model.error_occurred.connect(self.on_error_occurred)

        root = QtWidgets.QVBoxLayout()
        root.setContentsMargins(QtCore.QMargins(48, 0, 48, 0))

        root.addStretch(5)
        root.addWidget(self._title_label)
        root.addStretch(1)
        root.addWidget(self._scan_button)
        root.addWidget(self._loading_spinner)
        root.addWidget(self._error_label)
        root.addStretch(1)
        root.addWidget(QtWidgets.QLabel("Available Sensors:"))
        root.addWidget(self._sensor_list)
        root.addWidget(self._done_button)
        root.addStretch(5)

        self.setLayout(root)

    @override
    def on_destroy(self) -> None:
        self._done_button.clicked.disconnect(self._view_model.on_done_button_clicked)

        self._view_model.sensors_updated.disconnect(self.on_sensors_updated)
        self._view_model.scanning_changed.disconnect(self.on_scanning_changed)
        self._view_model.error_occurred.disconnect(self.on_error_occurred)

    @QtCore.Slot(list)
    def on_sensors_updated(self, sensors: list[str]) -> None:
        self._sensor_list.clear()
        if sensors:
            self._sensor_list.addItems(sensors)
        else:
            self._sensor_list.addItem("No sensors found")

    @QtCore.Slot(bool)
    def on_scanning_changed(self, is_scanning: bool) -> None:
        self._scan_button.setDisabled(is_scanning)
        self._loading_spinner.setVisible(is_scanning)

    @QtCore.Slot(str)
    def on_error_occurred(self, error_message: str) -> None:
        self._error_label.setText(error_message)
        self._error_label.setVisible(True)
