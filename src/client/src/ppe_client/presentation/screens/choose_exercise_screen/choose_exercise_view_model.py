from PySide6 import QtCore


class ChooseExerciseViewModel(QtCore.QObject):
    exercises_updated = QtCore.Signal(list)

    _exercise: list[int]
    _selected_exercise: int

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._exercise = []
        self._selected_exercise = 0

    def update_exercises(self) -> None:
        self.exercises_updated.emit(["Hello", "World"])

    def get_selected_exercise_id(self) -> int:
        return self._selected_exercise

    def select_exercise(self, index: int) -> None:
        self._selected_exercise = index
