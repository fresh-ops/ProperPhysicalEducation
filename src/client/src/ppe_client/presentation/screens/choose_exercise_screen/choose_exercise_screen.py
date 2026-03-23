from typing import override

from PySide6 import QtCore, QtWidgets

from ppe_client.adapters.network import ExerciseSession

from ...routing import Route, Screen
from ..cameras_screen.cameras_payload import CamerasPayload
from .choose_exercise_payload import ChooseExercisePayload
from .choose_exercise_view_model import ChooseExerciseViewModel


class ChooseExerciseScreen(Screen[ChooseExercisePayload]):
    def __init__(
        self, exercise_session: ExerciseSession, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent=parent)
        self._vm = ChooseExerciseViewModel(exercise_session)
        self._vm.exercises_updated.connect(self._on_exercise_options_updated)

        self._label = QtWidgets.QLabel("Welcome to PPE")
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._label.setStyleSheet("font-size: 24px;font-weight: bold;color: #333;")

        self._exercise_options = QtWidgets.QComboBox()
        self._exercise_options.currentIndexChanged.connect(self._on_exercise_selected)

        self._start_exercise_button = QtWidgets.QPushButton("Start")
        self._start_exercise_button.clicked.connect(self._on_start_button_clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins(48, 0, 48, 0))

        layout.addStretch(5)
        layout.addWidget(self._label)
        layout.addStretch(1)
        layout.addWidget(self._exercise_options)
        layout.addWidget(self._start_exercise_button)
        layout.addStretch(5)

        self.setLayout(layout)

    @override
    def on_enter(self, payload: ChooseExercisePayload | None = None) -> None:
        self._vm.update_exercises()
        return super().on_enter(payload)

    @QtCore.Slot()
    def _on_start_button_clicked(self) -> None:
        selected_exercise = self._vm.get_selected_exercise_id()
        self.request_navigation(
            Route.CAMERAS, CamerasPayload(exercise_id=selected_exercise)
        )

    @QtCore.Slot(int)
    def _on_exercise_selected(self, selected_index: int) -> None:
        self._vm.select_exercise(selected_index)

    @QtCore.Slot(list)
    def _on_exercise_options_updated(self, exercises: list[str]) -> None:
        self._exercise_options.clear()
        self._exercise_options.addItems(exercises)
