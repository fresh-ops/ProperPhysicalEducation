from abc import ABC, abstractmethod

from domain.model.pose import Pose
from domain.model.pose_id import PoseId


class PoseRepository(ABC):
    @abstractmethod
    def get_by_id(self, pose_id: PoseId) -> Pose:
        """
        Абстрактный метод для получения позы по ее идентификатору.

        Args:
            pose_id (PoseId): идентификатор позы

        Returns:
            Pose: объект позы, соответствующий заданному идентификатору
        """
        pass
