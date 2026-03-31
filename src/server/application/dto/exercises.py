from dataclasses import dataclass


@dataclass
class ExerciseItemDto:
    exercise_id: str
    name: str


@dataclass
class ExercisesResponseDto:
    exercises: list[ExerciseItemDto]
