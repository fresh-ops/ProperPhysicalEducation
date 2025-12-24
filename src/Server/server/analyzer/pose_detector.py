from typing import List
from analyzer.poses.pose import Pose

class PoseDetector:
    poses: List[Pose]

    def __init__(self, poses: List[Pose]):
        """
        Инициализация детектора поз
        
        Args:
            poses (List[Pose]): список эталонных поз
        """
        self.poses = poses

    def detect_pose(self, pose: Pose) -> List[Pose]:
        """
        Находит список эталонных поз, которые совпадают с данной позой
        
        Args:
            pose (Pose): поза для сопаставления
            
        Returns:
            List[Pose]: список подходящих поз
        """
        return [detected for detected in self.poses if detected == pose]
