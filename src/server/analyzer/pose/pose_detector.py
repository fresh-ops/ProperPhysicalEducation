from typing import List
from analyzer.pose.pose_deviants import calculate_deviations
from model.pose import Pose

class PoseDetector:
    poses: List[Pose]

    def __init__(self, poses: List[Pose]):
        """
        Инициализация детектора поз
        
        Args:
            poses (List[Pose]): список эталонных поз
        """
        self.poses = poses

    def detect_closest_reference_pose(self, current_pose: Pose) -> Pose:
        deviations = calculate_deviations(current_pose, self.poses)
        closest_reference_pose = min(deviations.keys(), key=lambda p: sum(deviations[p]))
        return closest_reference_pose