from pathlib import Path

from domain.model.exercise import Exercise
from domain.model.exercise_id import ExerciseId
from domain.model.pose_id import PoseId
from domain.model.pose_rule import PoseRule
from domain.ports.errors import EntityNotFoundError
from domain.ports.exercise_repository import ExerciseRepository
import json
from infrastructure.persistence.json.errors import (
    InvalidDirectoryError,
    JsonParseError,
    JsonReadError,
)


class JsonExerciseRepository(ExerciseRepository):
    def __init__(self, directory_path: str) -> None:
        self._directory_path = Path(directory_path)
        if not self._directory_path.is_dir():
            raise InvalidDirectoryError(directory_path)
        self._cache: dict[ExerciseId, Exercise] = {}

    def get_by_id(self, exercise_id: ExerciseId) -> Exercise:
        if exercise_id in self._cache:
            return self._cache[exercise_id]

        exercise_path = self._directory_path / f"{exercise_id}.json"

        try:
            with open(exercise_path, "r", encoding="utf-8") as f:
                serialized_exercise = json.load(f)
        except FileNotFoundError:
            raise EntityNotFoundError("Exercise", exercise_id.id)
        except json.JSONDecodeError as e:
            raise JsonReadError(str(exercise_path), e)

        try:
            exercise = Exercise(
                id=ExerciseId(serialized_exercise["id"]),
                name=serialized_exercise["name"],
                poses=[PoseId(p) for p in serialized_exercise["poses"]],
                pose_rules=[
                    PoseRule(
                        id=PoseId(r["id"]),
                        feature=r["feature"],
                        operator=r["operator"],
                        value=r["value"],
                        message=r["message"],
                    )
                    for r in serialized_exercise.get("pose_rules", [])
                ],
            )
            self._cache[exercise_id] = exercise
            return exercise
        except (KeyError, TypeError, ValueError) as e:
            raise JsonParseError(str(exercise_path), e)
