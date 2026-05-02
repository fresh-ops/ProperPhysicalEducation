import json
from pathlib import Path

from domain.model.pose import Pose
from domain.model.pose_id import PoseId
from domain.ports.errors import EntityNotFoundError
from domain.ports.pose_repository import PoseRepository
from infrastructure.persistence.json.errors import (
    InvalidDirectoryError,
    JsonParseError,
    JsonReadError,
)


class JsonPoseRepository(PoseRepository):
    def __init__(self, directory_path: str) -> None:
        self._directory_path = Path(directory_path)
        if not self._directory_path.is_dir():
            raise InvalidDirectoryError(directory_path)
        self._cache: dict[PoseId, Pose] = {}

    def get_by_id(self, pose_id: PoseId) -> Pose:
        if pose_id in self._cache:
            return self._cache[pose_id]

        pose_path = self._directory_path / f"{pose_id}.json"

        try:
            with open(pose_path, "r", encoding="utf-8") as f:
                serialized_pose = json.load(f)
        except FileNotFoundError:
            raise EntityNotFoundError("Pose", pose_id.id)
        except json.JSONDecodeError as e:
            raise JsonReadError(str(pose_path), e)

        try:
            serialized_pose["id"] = PoseId(serialized_pose["id"])
            pose = Pose(**serialized_pose)
            self._cache[pose_id] = pose
            return pose
        except (KeyError, TypeError, ValueError) as e:
            raise JsonParseError(str(pose_path), e)
