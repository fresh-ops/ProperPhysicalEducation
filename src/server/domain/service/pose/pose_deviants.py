from domain.model.pose import Pose
from domain.model.angle import Angle


def calculate_deviations(
    current_pose: Pose, reference_pose: Pose
) -> dict[Angle, float]:
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


def calculate_deviations_with_threshold(
    current_pose: Pose, reference_pose: Pose
) -> dict[Angle, float]:
    """
    Вычисляет отклонения между текущей позой и эталонной позой с учетом порога допустимых отклонений.
    Args:
        current_pose (Pose): текущая поза
        reference_pose (Pose): эталонная поза
    Returns:
        Dict[Angle, float]: словарь, где ключ - угол, значение - отклонение с учетом порога
    """
    deviations: dict[Angle, float] = {}

    for angle, current_angle, (min_angle, max_angle) in zip(
        Angle,
        current_pose.get_angles_list(),
        reference_pose.get_angle_ranges().values(),
    ):
        if current_angle < min_angle:
            deviations[angle] = min_angle - current_angle
        elif current_angle > max_angle:
            deviations[angle] = current_angle - max_angle

    return deviations
