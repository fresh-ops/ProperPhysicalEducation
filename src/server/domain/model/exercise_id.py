from dataclasses import dataclass


@dataclass(frozen=True)
class ExerciseId:
    id: str
