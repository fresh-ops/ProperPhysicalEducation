from domain.ports.exercise_repository import ExerciseRepository
from application.dto.exercises import ExercisesResponseDto, ExerciseItemDto


class GetExercisesUseCase:
    def __init__(self, exercise_repository: ExerciseRepository):
        self.exercise_repository = exercise_repository

    def execute(self) -> ExercisesResponseDto:
        exercises = self.exercise_repository.get_all()
        return ExercisesResponseDto(
            exercises=[
                ExerciseItemDto(exercise_id=str(e.id), name=e.name) for e in exercises
            ]
        )
