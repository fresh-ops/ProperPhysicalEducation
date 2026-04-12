from typing import override

from PySide6 import QtCore, QtWidgets

from ...routing.core import Screen
from .sensor_calibration_view_model import SensorCalibrationViewModel


class SensorCalibrationScreen(Screen[SensorCalibrationViewModel]):
    @override
    def on_create(self) -> None:
        self._title_label = QtWidgets.QLabel("Calibrate Sensor")
        self._title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #333;"
        )

        self._instruction_label = QtWidgets.QLabel(
            "Press the button below to start calibration.\n"
            "You will be guided through two 5-second stages."
        )
        self._instruction_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._instruction_label.setWordWrap(True)
        self._instruction_label.setStyleSheet("font-size: 14px; color: #666;")

        self._stage_label = QtWidgets.QLabel()
        self._stage_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._stage_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1976d2;"
        )
        self._stage_label.setVisible(False)

        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1976d2;
            }
            """
        )

        self._timer_label = QtWidgets.QLabel()
        self._timer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._timer_label.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #333;"
        )
        self._timer_label.setVisible(False)

        self._error_label = QtWidgets.QLabel()
        self._error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self._error_label.setVisible(False)

        self._start_button = QtWidgets.QPushButton("Start Calibration")
        self._start_button.clicked.connect(
            self._view_model.on_start_calibration_clicked
        )

        self._view_model.stage_changed.connect(self._on_stage_changed)
        self._view_model.progress_changed.connect(self._on_progress_changed)
        self._view_model.calibration_complete.connect(self._on_calibration_complete)
        self._view_model.error_occurred.connect(self._on_error_occurred)

        root = QtWidgets.QVBoxLayout()
        root.setContentsMargins(QtCore.QMargins(48, 0, 48, 0))

        root.addStretch(3)
        root.addWidget(self._title_label)
        root.addStretch(1)
        root.addWidget(self._instruction_label)
        root.addStretch(2)
        root.addWidget(self._stage_label)
        root.addWidget(self._timer_label)
        root.addWidget(self._progress_bar)
        root.addWidget(self._error_label)
        root.addStretch(2)
        root.addWidget(self._start_button)
        root.addStretch(3)

        self.setLayout(root)

    @override
    def on_destroy(self) -> None:
        self._view_model.stage_changed.disconnect(self._on_stage_changed)
        self._view_model.progress_changed.disconnect(self._on_progress_changed)
        self._view_model.calibration_complete.disconnect(self._on_calibration_complete)
        self._view_model.error_occurred.disconnect(self._on_error_occurred)

    @QtCore.Slot(str)
    def _on_stage_changed(self, stage: str) -> None:
        self._stage_label.setVisible(True)
        self._timer_label.setVisible(True)
        self._progress_bar.setVisible(True)
        self._start_button.setDisabled(True)

        if stage == "relaxed":
            self._stage_label.setText("Stage 1: Relax Your Hand")
            self._stage_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #4caf50;"
            )
        elif stage == "tensed":
            self._stage_label.setText("Stage 2: Tense Your Hand Maximally")
            self._stage_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #ff9800;"
            )

    @QtCore.Slot(int)
    def _on_progress_changed(self, progress: int) -> None:
        self._progress_bar.setValue(progress)
        remaining = 5 - int(progress / 100 * 5)
        self._timer_label.setText(f"{remaining}s")

    @QtCore.Slot()
    def _on_calibration_complete(self) -> None:
        self._stage_label.setVisible(False)
        self._timer_label.setVisible(False)
        self._progress_bar.setVisible(False)
        self._start_button.setDisabled(False)

    @QtCore.Slot(str)
    def _on_error_occurred(self, error_message: str) -> None:
        self._error_label.setText(error_message)
        self._error_label.setVisible(True)
        self._start_button.setDisabled(False)
