import asyncio

from PySide6 import QtCore

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.network.schemas import ExerciseItem


class ChooseExerciseViewModel(QtCore.QObject):
    exercises_updated = QtCore.Signal(list)

    _exercise_session: ExerciseSession
    _exercises: list[ExerciseItem]
    _selected_exercise: ExerciseItem

    def __init__(
        self, exercise_session: ExerciseSession, parent: QtCore.QObject | None = None
    ) -> None:
        super().__init__(parent=parent)
        self._exercise_session = exercise_session
        self._exercises = []
        self._selected_exercise = ExerciseItem(id=0, name="")

    def update_exercises(self) -> None:
        loop = asyncio.get_running_loop()
        loop.create_task(  # noqa: RUF006
            self._exercise_session.get_exercises(self._on_exercises_loaded)
        )

    def _on_exercises_loaded(self, exercises: list[ExerciseItem]) -> None:
        print(exercises)
        self._exercises = exercises
        names = [e.name for e in self._exercises]
        self.exercises_updated.emit(names)

    def get_selected_exercise_id(self) -> int:
        return self._selected_exercise.id

    def select_exercise(self, index: int) -> None:
        self._selected_exercise = self._exercises[index]
        print(self._selected_exercise)
