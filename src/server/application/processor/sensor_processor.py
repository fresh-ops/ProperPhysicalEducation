from abc import ABC, abstractmethod
from typing import Tuple

from domain.model.exercise_state import ExerciseState
from domain.model.feedback import Feedback


class SensorProcessor[T](ABC):
    @abstractmethod
    def process(
        self, data: T, state: ExerciseState
    ) -> Tuple[list[Feedback], ExerciseState]:
        pass
