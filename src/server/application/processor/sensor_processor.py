from abc import ABC, abstractmethod
from typing import Tuple

from application.processor.process_context import ProcessContext
from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.feedback import Feedback


class SensorProcessor(ABC):
    @abstractmethod
    def process(
        self, context: ProcessContext, state: ExerciseState
    ) -> Tuple[list[Feedback], ExerciseState]:
        pass


class SensorProcessorFactory(ABC):
    @abstractmethod
    def create(self, exercise_id: ExerciseId) -> SensorProcessor:
        pass
