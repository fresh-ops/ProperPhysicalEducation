from abc import ABC, abstractmethod

from domain.model.pose import Pose
from domain.model.pose_match_result import PoseMatchResult


class PoseMatcherStrategy(ABC):
    @abstractmethod
    def match(self, current_pose: Pose, reference_poses: list[Pose]) -> PoseMatchResult:
        """
        Абстрактный метод для сравнения текущей позы с эталонной позой и получения результата соответствия.

        Args:
            current_pose (Pose): текущая поза
            reference_poses (list[Pose]): список эталонных поз

        Returns:
            PoseMatchResult: результат соответствия поз
        """
        pass
