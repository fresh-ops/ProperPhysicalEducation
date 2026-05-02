from typing import override

from PySide6 import QtCore, QtWidgets

from ...routing.core import Screen
from .choose_exercise_view_model import ChooseExerciseViewModel


class ChooseExerciseScreen(Screen[ChooseExerciseViewModel]):
    @override
    def on_create(self) -> None:
        self._label = QtWidgets.QLabel("Welcome to PPE")
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._label.setStyleSheet("font-size: 24px;font-weight: bold;color: #333;")

        self._exercise_options = QtWidgets.QComboBox()
        self._exercise_options.currentIndexChanged.connect(
            self._view_model.on_selected_exercise_change
        )
        self._view_model.exercises_updated.connect(self.on_exercises_updated)

        self._start_exercise_button = QtWidgets.QPushButton("Start")
        self._start_exercise_button.clicked.connect(
            self._view_model.on_start_exercise_button_clicked
        )
        self._view_model.start_button_disabled_set.connect(
            self.on_start_button_disabled_set
        )
        # self._start_exercise_button.clicked.connect(self._on_start_button_clicked)

        root = QtWidgets.QVBoxLayout()
        root.setContentsMargins(QtCore.QMargins(48, 0, 48, 0))

        root.addStretch(5)
        root.addWidget(self._label)
        root.addStretch(1)
        root.addWidget(self._exercise_options)
        root.addWidget(self._start_exercise_button)
        root.addStretch(5)

        self.setLayout(root)

    @override
    def on_destroy(self) -> None:
        self._view_model.exercises_updated.disconnect(self.on_exercises_updated)
        self._start_exercise_button.clicked.disconnect(
            self._view_model.on_start_exercise_button_clicked
        )
        self._view_model.start_button_disabled_set.disconnect(
            self.on_start_button_disabled_set
        )

    @QtCore.Slot(list)
    def on_exercises_updated(self, exercises: list[str]) -> None:
        self._exercise_options.clear()
        self._exercise_options.addItems(exercises)

    @QtCore.Slot(bool)
    def on_start_button_disabled_set(self, disabled: bool) -> None:
        self._start_exercise_button.setDisabled(disabled)
