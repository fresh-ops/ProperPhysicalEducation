from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.network.schemas import ExerciseItem
from ppe_client.presentation.routing.routes import Routes
from ppe_client.presentation.screens.training.training_payload import TrainingPayload

from ...routing.core import ViewModel
from ..sensor_discovery import SensorDiscoveryPayload
from .choose_exercise_payload import ChooseExercisePayload


@injectable
class ChooseExerciseViewModel(ViewModel[ChooseExercisePayload]):
    exercises_updated = QtCore.Signal(list)
    start_button_disabled_set = QtCore.Signal(bool)

    _exercise_session: ExerciseSession
    _exercises: list[ExerciseItem]
    _selected_exersice: ExerciseItem

    def __init__(self, exersice_session: ExerciseSession) -> None:
        super().__init__()
        self._exercise_session = exersice_session
        self._exercises = []

    @override
    async def on_enter(self, payload: ChooseExercisePayload | None = None) -> None:
        self.start_button_disabled_set.emit(True)
        self._exercises = await self._exercise_session.get_exercises()
        exercise_names = [e.name for e in self._exercises]
        self.exercises_updated.emit(exercise_names)

    @QtCore.Slot(int)
    def on_selected_exercise_change(self, exercise_index: int) -> None:
        self._selected_exersice = self._exercises[exercise_index]
        self.start_button_disabled_set.emit(False)

    @QtCore.Slot()
    def on_start_exercise_button_clicked(self) -> None:
        self.request_navigation(
            Routes.TRAINING,
            TrainingPayload(exercise_id=self._selected_exersice.exercise_id),
        )

    @QtCore.Slot()
    def on_connect_sensors_button_clicked(self) -> None:
        self.request_navigation(Routes.SENSOR_DISCOVERY, SensorDiscoveryPayload())
