from typing import Dict, List
from poses.pose import Pose


class PoseDeviants:
    """
    Класс для вычисления отклонений между текущей позой и эталонными позами.
    """
    
    def __init__(self, pose_detector, angle_analyzer):
        """
        Инициализация анализатора отклонений поз.
        
        Args:
            pose_detector: детектор поз
            angle_analyzer: анализатор углов для получения текущей позы
        """
        self.pose_detector = pose_detector
        self.angle_analyzer = angle_analyzer
    
    def calculate_deviations(self) -> Dict[Pose, List[float]]:
        """
        Вычисляет отклонения между текущей позой и эталонными позами.
        
        Returns:
            Dict[Pose, List[float]]: словарь, где ключ - эталонная поза,
                                    значение - массив отклонений по каждому углу
                                    [left_shoulder, right_shoulder, left_elbow, 
                                     right_elbow, left_knee, right_knee]
        """
        current_pose = self.angle_analyzer.get_current_pose()
        detected_poses = self.pose_detector.detect_pose(current_pose)
        
        deviations = {}
        
        for reference_pose in detected_poses:
            current_angles = current_pose.get_angles_list()
            reference_angles = reference_pose.get_angles_list()
            
            deviations[reference_pose] = [
                abs(curr_angle - ref_angle)
                for curr_angle, ref_angle in zip(current_angles, reference_angles)
            ]
        
        return deviations