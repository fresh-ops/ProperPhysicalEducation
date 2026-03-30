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


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def pose_repository(temp_dir: Path) -> JsonPoseRepository:
    return JsonPoseRepository(str(temp_dir))


def test_get_by_id_valid(pose_repository: JsonPoseRepository, temp_dir: Path) -> None:
    pose_id = PoseId("test_pose")
    valid_pose_data = {
        "id": pose_id,
        "name": "Test Pose",
        "threshold": 10.0,
        "left_hip_angle": 165.0,
        "right_hip_angle": 165.0,
        "left_shoulder_angle": 0.0,
        "right_shoulder_angle": 0.0,
        "left_elbow_angle": 180.0,
        "right_elbow_angle": 180.0,
        "left_knee_angle": 180.0,
        "right_knee_angle": 180.0,
    }
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
        pose_repository.get_by_id(PoseId("non_existent_pose"))
    assert "Pose with id 'non_existent_pose' not found" in str(exc_info.value)


def test_get_by_id_invalid_json(
    pose_repository: JsonPoseRepository, temp_dir: Path
) -> None:
    pose_id = PoseId("invalid_pose")
    invalid_json_content = "{invalid_json: true"
    pose_file = temp_dir / f"{pose_id}.json"
    with open(pose_file, "w", encoding="utf-8") as f:
        f.write(invalid_json_content)

    with pytest.raises(JsonReadError) as exc_info:
        pose_repository.get_by_id(pose_id)
    assert "Error reading" in str(exc_info.value)


def test_get_by_id_invalid_pose_data(
    pose_repository: JsonPoseRepository, temp_dir: Path
) -> None:
    pose_id = PoseId("invalid_pose_data")
    invalid_pose_data = {
        "id": pose_id,
        "name": "Invalid Pose",
        "threshold": "not_a_number",
        "left_hip_angle": 165.0,
        "right_hip_angle": 165.0,
        "left_shoulder_angle": 0.0,
        "right_shoulder_angle": 0.0,
        "left_elbow_angle": 180.0,
        "right_elbow_angle": 180.0,
        "left_knee_angle": 180.0,
        "right_knee_angle": 180.0,
    }
    pose_file = temp_dir / f"{pose_id}.json"
    with open(pose_file, "w", encoding="utf-8") as f:
        json.dump(invalid_pose_data, f)

    with pytest.raises(JsonParseError) as exc_info:
        pose_repository.get_by_id(pose_id)
    assert "Error parsing" in str(exc_info.value)
