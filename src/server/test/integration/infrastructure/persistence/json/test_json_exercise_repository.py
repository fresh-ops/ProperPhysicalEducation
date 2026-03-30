import json
from collections.abc import Iterator
from pathlib import Path
import tempfile

import pytest

from domain.model.exercise_id import ExerciseId
from domain.ports.errors import EntityNotFoundError
from infrastructure.persistence.json.errors import JsonParseError, JsonReadError
from infrastructure.persistence.json.repository.json_exercise_repository import (
    JsonExerciseRepository,
)


TEST_EXERCISE_ID = "test_exercise"
TEST_EXERCISE_NAME = "Test Exercise"
NON_EXISTENT_EXERCISE_ID = "non_existent_exercise"

INVALID_JSON_EXERCISE_ID = "invalid_exercise"
INVALID_JSON_CONTENT = "{invalid_json: true"

INVALID_EXERCISE_DATA_ID = "invalid_exercise_data"
INVALID_EXERCISE_DATA_NAME = "Invalid Exercise"
INVALID_EXERCISE_RULES_VALUE = "this should be a list, not a string"

EXERCISE_ERROR_FRAGMENT = "Exercise"
JSON_READ_ERROR_FRAGMENT = "Error reading"
JSON_PARSE_ERROR_FRAGMENT = "Error parsing"


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def exercise_repository(temp_dir: Path) -> JsonExerciseRepository:
    return JsonExerciseRepository(str(temp_dir))


@pytest.fixture
def valid_exercise_data() -> dict[str, object]:
    return {
        "id": TEST_EXERCISE_ID,
        "name": TEST_EXERCISE_NAME,
        "poses": [],
        "rules": [],
    }


@pytest.fixture
def invalid_exercise_data() -> dict[str, object]:
    return {
        "id": INVALID_EXERCISE_DATA_ID,
        "name": INVALID_EXERCISE_DATA_NAME,
        "poses": [],
        "rules": INVALID_EXERCISE_RULES_VALUE,
    }


def test_get_by_id_valid(
    exercise_repository: JsonExerciseRepository,
    temp_dir: Path,
    valid_exercise_data: dict[str, object],
) -> None:
    exercise_id = ExerciseId(TEST_EXERCISE_ID)
    exercise_file = temp_dir / f"{exercise_id}.json"
    with open(exercise_file, "w", encoding="utf-8") as f:
        json.dump(valid_exercise_data, f)

    exercise = exercise_repository.get_by_id(exercise_id)
    assert exercise.id == TEST_EXERCISE_ID
    assert exercise.name == TEST_EXERCISE_NAME


def test_get_by_id_not_found(exercise_repository: JsonExerciseRepository) -> None:
    with pytest.raises(EntityNotFoundError) as exc_info:
        exercise_repository.get_by_id(ExerciseId(NON_EXISTENT_EXERCISE_ID))
    assert EXERCISE_ERROR_FRAGMENT in str(exc_info.value)


def test_get_by_id_invalid_json(
    exercise_repository: JsonExerciseRepository, temp_dir: Path
) -> None:
    exercise_id = ExerciseId(INVALID_JSON_EXERCISE_ID)
    exercise_file = temp_dir / f"{exercise_id}.json"
    with open(exercise_file, "w", encoding="utf-8") as f:
        f.write(INVALID_JSON_CONTENT)

    with pytest.raises(JsonReadError) as exc_info:
        exercise_repository.get_by_id(exercise_id)
    assert JSON_READ_ERROR_FRAGMENT in str(exc_info.value)


def test_get_by_id_invalid_exercise_data(
    exercise_repository: JsonExerciseRepository,
    temp_dir: Path,
    invalid_exercise_data: dict[str, object],
) -> None:
    exercise_id = ExerciseId(INVALID_EXERCISE_DATA_ID)
    exercise_file = temp_dir / f"{exercise_id}.json"
    with open(exercise_file, "w", encoding="utf-8") as f:
        json.dump(invalid_exercise_data, f)

    with pytest.raises(JsonParseError) as exc_info:
        exercise_repository.get_by_id(exercise_id)
    assert JSON_PARSE_ERROR_FRAGMENT in str(exc_info.value)
