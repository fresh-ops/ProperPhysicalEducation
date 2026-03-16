from analyzer.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)
from model.pose import Pose
from model.pose_match_result import PoseMatchResult


class PoseMatcher:
    reference_poses: list[Pose]

    def __init__(self, reference_poses: list[Pose], strategy: PoseMatcherStrategy):
        """
        Args:
            reference_poses (List[Pose]): список эталонных поз
            strategy (PoseMatcherStrategy): стратегия сравнения поз
        """
        self.reference_poses = reference_poses
        self.strategy = strategy

    def match(self, current_pose: Pose) -> PoseMatchResult:
        """
        Находит ближайшую эталонную позу для заданной текущей позы с учетом отклонений.

        Args:
            current_pose (Pose): текущая поза

        Returns:
            PoseMatchResult: результат соответствия поз
        """
        return self.strategy.match(current_pose, self.reference_poses)
