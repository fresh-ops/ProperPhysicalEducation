from dataclasses import dataclass
from domain.model.exercise_id import ExerciseId
from domain.model.pose_id import PoseId
from domain.model.pose_rule import PoseRule


@dataclass(frozen=True)
class Exercise:
    """
    Класс упражнения.

    Fields:
        id (ExerciseId): идентификатор упражнения
        name (str): имя упражнения
        poses (list[PoseId]): список эталонных поз для этого упражнения
        pose_rules (list[PoseRule]): список правил для этого упражнения
    """

    id: ExerciseId
    name: str
    poses: list[PoseId]
    pose_rules: list[PoseRule]

    def __post_init__(self) -> None:
        self._validate_id()
        self._validate_name()
        self._validate_poses()
        self._validate_pose_rules()

    def _validate_id(self) -> None:
        if not isinstance(self.id, ExerciseId):
            raise TypeError(f"id must be ExerciseId, got {type(self.id).__name__}")

    def _validate_name(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise TypeError(f"name must be str, got {type(self.name).__name__}")

    def _validate_poses(self) -> None:
        if not isinstance(self.poses, list):
            raise TypeError(f"poses must be a list, got {type(self.poses).__name__}")
        for pose in self.poses:
            if not isinstance(pose, PoseId):
                raise TypeError(
                    f"Each pose must be an instance of PoseId, got {type(pose).__name__}"
                )

    def _validate_pose_rules(self) -> None:
        if not isinstance(self.pose_rules, list):
            raise TypeError(
                f"pose_rules must be a list, got {type(self.pose_rules).__name__}"
            )
        for rule in self.pose_rules:
            if not isinstance(rule, PoseRule):
                raise TypeError(
                    f"Each rule must be an instance of PoseRule, got {type(rule).__name__}"
                )
            if rule.id not in self.poses:
                raise ValueError(
                    f"Rule references pose '{rule.id}' not in exercise poses"
                )
