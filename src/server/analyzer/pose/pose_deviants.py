from model.pose import Pose
from analyzer.pose.skeleton_transformer.skeleton import Angle


def calculate_deviations(current_pose: Pose, reference_pose: Pose) -> dict[Angle, float]:
    """
    Вычисляет отклонения между текущей позой и эталонной позой.
    Args:
        current_pose (Pose): текущая поза
        reference_pose (Pose): эталонная поза
    Returns:
        Dict[Angle, float]: словарь, где ключ - угол, значение - отклонение
    """
    return {
        angle: abs(current_angle - reference_angle)
        for angle, current_angle, reference_angle in zip(
            Angle,
            current_pose.get_angles_list(),
            reference_pose.get_angles_list(),
        )
    }
