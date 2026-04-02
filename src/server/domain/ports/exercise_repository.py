from abc import ABC, abstractmethod

from domain.model.exercise import Exercise
from domain.model.exercise_id import ExerciseId


class ExerciseRepository(ABC):
    @abstractmethod
    def get_by_id(self, exercise_id: ExerciseId) -> Exercise:
        """
        Абстрактный метод для получения упражнения по его идентификатору.

        Args:
            exercise_id (ExerciseId): идентификатор упражнения

        Returns:
            Exercise: объект упражнения, соответствующий заданному идентификатору
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Exercise]:
        """
        Абстрактный метод для получения всех упражнений.

        Returns:
            list[Exercise]: список всех упражнений
        """
        pass
