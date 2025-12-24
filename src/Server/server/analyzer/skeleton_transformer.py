import math
from typing import List
from analyzer.poses.pose import Pose
from analyzer.skeleton import Angle

def calculate_angle_xy(skeleton: List[List[float]], angle: Angle) -> float:
    """
    Вычисляет угол angle В ПЛОСКОСТИ XY (плоская проекция, Z игнорируется)

    Args:
        skeleton (List[List[float]]): матрица точек цифрового скелета. Каждый элемент внешнего списка представляет собой набор координат [x, y, z]
        angle (Angle): угол, который требуется вычислить

    Returns:
        float: угол в градусах (0-180)
    """
    p1_idx = angle.side_a.index
    p2_idx = angle.vertex.index
    p3_idx = angle.side_b.index

    p1 = skeleton[p1_idx]
    p2 = skeleton[p2_idx]
    p3 = skeleton[p3_idx]

    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])


    v1_len = math.sqrt(v1[0]**2 + v1[1]**2)
    v2_len = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if v1_len < 1e-6 or v2_len < 1e-6:

        return 0.0

    angle1 = math.atan2(v1[1], v1[0])
    angle2 = math.atan2(v2[1], v2[0])

    angle_diff = abs(angle1 - angle2)

    if angle_diff > math.pi:
        angle_diff = 2 * math.pi - angle_diff

    return math.degrees(angle_diff)

def landmarks_to_pose(skeleton: List[List[float]]) -> Pose:
    """
    Переводит точки цифрового скелета в объект Pose

    Args:
        skeleton (List[List[float]]): матрица точек цифрового скелета. Каждый элемент внешнего списка представляет собой набор координат [x, y, z]

    Returns:
        Pose: объект позы с вычисленными углами, пустым именем и нулевым порогом
    """
    return Pose(
        name="",
        threshold=0.0,
        left_shoulder_angle=calculate_angle_xy(skeleton, Angle.LEFT_SHOULDER),
        right_shoulder_angle=calculate_angle_xy(skeleton, Angle.RIGHT_SHOULDER),
        left_elbow_angle=calculate_angle_xy(skeleton, Angle.LEFT_ELBOW),
        right_elbow_angle=calculate_angle_xy(skeleton, Angle.RIGHT_ELBOW),
        left_knee_angle=calculate_angle_xy(skeleton, Angle.LEFT_KNEE),
        right_knee_angle=calculate_angle_xy(skeleton, Angle.RIGHT_KNEE)
    )
