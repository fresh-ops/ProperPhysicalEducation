from dataclasses import dataclass
from domain.model.exercise_id import ExerciseId
from domain.model.pose_id import PoseId
from domain.model.rule import Rule


@dataclass(frozen=True)
class Exercise:
    """
    Класс упражнения.

    Fields:
        id (ExerciseId): идентификатор упражнения
        name (str): имя упражнения
        poses (list[PoseId]): список эталонных поз для этого упражнения
        rules (list[Rule]): список правил для этого упражнения
    """

    id: ExerciseId
    name: str
    poses: list[PoseId]
    rules: list[Rule]

    def __post_init__(self) -> None:
        self._validate_id()
        self._validate_name()
        self._validate_poses()
        self._validate_rules()

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

    def _validate_rules(self) -> None:
        if not isinstance(self.rules, list):
            raise TypeError(f"rules must be a list, got {type(self.rules).__name__}")
        for rule in self.rules:
            if not isinstance(rule, Rule):
                raise TypeError(
                    f"Each rule must be an instance of Rule, got {type(rule).__name__}"
                )
            if rule.pose_id not in self.poses:
                raise ValueError(
                    f"Rule references pose '{rule.pose_id}' not in exercise poses"
                )
