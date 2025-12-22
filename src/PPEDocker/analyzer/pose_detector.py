from typing import List
from poses.pose import Pose

class PoseDetector:
    def __init__(self, poses: List[Pose]):
        """
        Инициализация детектора поз
        
        Args:
            poses (List[Pose]): список эталонных поз
        """
        self.poses = poses


    def detect_pose(self, pose) -> List[Pose]:
        """
        Определяет текущую позу на основе углов из AngleAnalyzer
        
        Args:
            angle_analyzer: Экземпляр AngleAnalyzer с вычисленными углами
            
        Returns:
            Dict: Данные позы в формате массива
        """
        return [detected for detected in self.poses if detected == pose]
