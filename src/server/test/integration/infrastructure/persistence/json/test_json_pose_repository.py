import json
from collections.abc import Iterator
from pathlib import Path
import tempfile

import pytest

from domain.model.pose_id import PoseId
from domain.ports.errors import EntityNotFoundError
from infrastructure.persistence.json.errors import JsonParseError, JsonReadError
from infrastructure.persistence.json.repository.json_pose_repository import (
    JsonPoseRepository,
)


TEST_POSE_ID = "test_pose"
TEST_POSE_NAME = "Test Pose"
TEST_POSE_THRESHOLD = 10.0
TEST_LEFT_HIP_ANGLE = 165.0
TEST_RIGHT_HIP_ANGLE = 165.0
TEST_LEFT_SHOULDER_ANGLE = 0.0
TEST_RIGHT_SHOULDER_ANGLE = 0.0
TEST_LEFT_ELBOW_ANGLE = 180.0
TEST_RIGHT_ELBOW_ANGLE = 180.0
TEST_LEFT_KNEE_ANGLE = 180.0
TEST_RIGHT_KNEE_ANGLE = 180.0

NON_EXISTENT_POSE_ID = "non_existent_pose"
NON_EXISTENT_POSE_ERROR = f"Pose with id '{NON_EXISTENT_POSE_ID}' not found"

INVALID_JSON_POSE_ID = "invalid_pose"
INVALID_JSON_CONTENT = "{invalid_json: true"

INVALID_POSE_DATA_ID = "invalid_pose_data"
INVALID_POSE_DATA_NAME = "Invalid Pose"
INVALID_POSE_THRESHOLD = "not_a_number"

JSON_READ_ERROR_FRAGMENT = "Error reading"
JSON_PARSE_ERROR_FRAGMENT = "Error parsing"


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def pose_repository(temp_dir: Path) -> JsonPoseRepository:
    return JsonPoseRepository(str(temp_dir))


@pytest.fixture
def valid_pose_data() -> dict[str, object]:
    return {
        "id": TEST_POSE_ID,
        "name": TEST_POSE_NAME,
        "threshold": TEST_POSE_THRESHOLD,
        "left_hip_angle": TEST_LEFT_HIP_ANGLE,
        "right_hip_angle": TEST_RIGHT_HIP_ANGLE,
        "left_shoulder_angle": TEST_LEFT_SHOULDER_ANGLE,
        "right_shoulder_angle": TEST_RIGHT_SHOULDER_ANGLE,
        "left_elbow_angle": TEST_LEFT_ELBOW_ANGLE,
        "right_elbow_angle": TEST_RIGHT_ELBOW_ANGLE,
        "left_knee_angle": TEST_LEFT_KNEE_ANGLE,
        "right_knee_angle": TEST_RIGHT_KNEE_ANGLE,
    }


@pytest.fixture
def invalid_pose_data() -> dict[str, object]:
    return {
        "id": INVALID_POSE_DATA_ID,
        "name": INVALID_POSE_DATA_NAME,
        "threshold": INVALID_POSE_THRESHOLD,
        "left_hip_angle": TEST_LEFT_HIP_ANGLE,
        "right_hip_angle": TEST_RIGHT_HIP_ANGLE,
        "left_shoulder_angle": TEST_LEFT_SHOULDER_ANGLE,
        "right_shoulder_angle": TEST_RIGHT_SHOULDER_ANGLE,
        "left_elbow_angle": TEST_LEFT_ELBOW_ANGLE,
        "right_elbow_angle": TEST_RIGHT_ELBOW_ANGLE,
        "left_knee_angle": TEST_LEFT_KNEE_ANGLE,
        "right_knee_angle": TEST_RIGHT_KNEE_ANGLE,
    }


def test_get_by_id_valid(
    pose_repository: JsonPoseRepository,
    temp_dir: Path,
    valid_pose_data: dict[str, object],
) -> None:
    pose_id = PoseId(TEST_POSE_ID)
    pose_file = temp_dir / f"{pose_id}.json"
    with open(pose_file, "w", encoding="utf-8") as f:
        json.dump(valid_pose_data, f)

    pose = pose_repository.get_by_id(pose_id)

    assert pose.id == pose_id.id
    assert pose.name == valid_pose_data["name"]
    assert pose.threshold == valid_pose_data["threshold"]
    assert pose.left_hip_angle == valid_pose_data["left_hip_angle"]
    assert pose.right_hip_angle == valid_pose_data["right_hip_angle"]
    assert pose.left_shoulder_angle == valid_pose_data["left_shoulder_angle"]
    assert pose.right_shoulder_angle == valid_pose_data["right_shoulder_angle"]
    assert pose.left_elbow_angle == valid_pose_data["left_elbow_angle"]
    assert pose.right_elbow_angle == valid_pose_data["right_elbow_angle"]
    assert pose.left_knee_angle == valid_pose_data["left_knee_angle"]
    assert pose.right_knee_angle == valid_pose_data["right_knee_angle"]


def test_get_by_id_not_found(pose_repository: JsonPoseRepository) -> None:
    with pytest.raises(EntityNotFoundError) as exc_info:
        pose_repository.get_by_id(PoseId(NON_EXISTENT_POSE_ID))
    assert NON_EXISTENT_POSE_ERROR in str(exc_info.value)


def test_get_by_id_invalid_json(
    pose_repository: JsonPoseRepository, temp_dir: Path
) -> None:
    pose_id = PoseId(INVALID_JSON_POSE_ID)
    pose_file = temp_dir / f"{pose_id}.json"
    with open(pose_file, "w", encoding="utf-8") as f:
        f.write(INVALID_JSON_CONTENT)

    with pytest.raises(JsonReadError) as exc_info:
        pose_repository.get_by_id(pose_id)
    assert JSON_READ_ERROR_FRAGMENT in str(exc_info.value)


def test_get_by_id_invalid_pose_data(
    pose_repository: JsonPoseRepository,
    temp_dir: Path,
    invalid_pose_data: dict[str, object],
) -> None:
    pose_id = PoseId(INVALID_POSE_DATA_ID)
    pose_file = temp_dir / f"{pose_id}.json"
    with open(pose_file, "w", encoding="utf-8") as f:
        json.dump(invalid_pose_data, f)

    with pytest.raises(JsonParseError) as exc_info:
        pose_repository.get_by_id(pose_id)
    assert JSON_PARSE_ERROR_FRAGMENT in str(exc_info.value)
