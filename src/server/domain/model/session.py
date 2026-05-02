from dataclasses import dataclass, replace

from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.session_id import SessionId


@dataclass(frozen=True)
class Session:
    session_id: SessionId
    exercise_id: ExerciseId
    exercise_state: ExerciseState

    def update(self, new_state: ExerciseState) -> "Session":
        return replace(self, exercise_state=new_state)
