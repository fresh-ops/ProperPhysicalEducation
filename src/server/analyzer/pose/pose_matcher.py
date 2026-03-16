from dataclasses import dataclass
from analyzer.pose.pose_deviants import calculate_deviations
from analyzer.pose.skeleton_transformer.skeleton import Angle
from model.pose import Pose


@dataclass
class PoseMatchResult:
    reference_pose: Pose
    deviations: dict[Angle, float]


class PoseMatcher:
    poses: list[Pose]

    def __init__(self, poses: list[Pose]):
        """
        Args:
            poses (List[Pose]): список эталонных поз
        """
        self.poses = poses


    def match(self, current_pose: Pose) -> PoseMatchResult:
        """
        Находит ближайшую эталонную позу для заданной текущей позы с учетом отклонений.

        Args:
            current_pose (Pose): текущая поза

        Returns:
            PoseMatchResult: результат соответствия поз
        """

        matched_pose = None
        min_penalty = float('inf')

        for reference_pose in self.poses:
            penalty = self.__calculate_penalty(current_pose, reference_pose)
            if penalty < min_penalty:
                min_penalty = penalty
                matched_pose = reference_pose

        if matched_pose is None:
            raise ValueError("No reference pose found for the current pose.")

        deviations = calculate_deviations(current_pose, matched_pose)


        return PoseMatchResult(
            reference_pose=matched_pose, 
            deviations=deviations
        )


    def __calculate_penalty(self, current_pose: Pose, reference_pose: Pose) -> float:
        """
        Вычисляет штраф за отклонение от эталонной позы.

        Args:
            current_pose (Pose): текущая поза
            reference_pose (Pose): эталонная поза

        Returns:
            float: штраф за отклонение
        """
        current_pose_angles = current_pose.get_angles_list()
        reference_pose_angles_ranges = reference_pose.get_angle_ranges()

        penalty = 0.0
        for current_angle, (min_angle, max_angle) in zip(current_pose_angles, reference_pose_angles_ranges.values()):
            if current_angle < min_angle:
                penalty += min_angle - current_angle
            elif current_angle > max_angle:
                penalty += current_angle - max_angle

        return penalty
