from typing import Dict, List
from poses.pose import Pose


def calculate_deviations(current_pose: Pose, poses: List[Pose]) -> Dict[Pose, List[float]]:
    """
    Вычисляет отклонения между текущей позой и эталонными позами.
    
    Returns:
        Dict[Pose, List[float]]: словарь, где ключ - эталонная поза,
                                значение - массив отклонений по каждому углу
                                [left_shoulder, right_shoulder, left_elbow, 
                                 right_elbow, left_knee, right_knee]
    """
    deviations = {}
    
    for reference_pose in poses:
        current_angles = current_pose.get_angles_list()
        reference_angles = reference_pose.get_angles_list()
        
        deviations[reference_pose.name] = [
            abs(curr_angle - ref_angle)
            for curr_angle, ref_angle in zip(current_angles, reference_angles)
        ]
    
    return deviations
