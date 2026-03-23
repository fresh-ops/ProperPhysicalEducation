from analyzer.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)
from model.pose import Pose
from model.pose_match_result import PoseMatchResult
from analyzer.pose.pose_deviants import calculate_deviations_with_threshold


class PenaltyStrategy(PoseMatcherStrategy):
    def match(self, current_pose: Pose, reference_poses: list[Pose]) -> PoseMatchResult:
        best_match = None
        min_penalty = float("inf")

        for reference_pose in reference_poses:
            deviations = calculate_deviations_with_threshold(
                current_pose, reference_pose
            )
            penalty = sum(deviations.values())

            if penalty < min_penalty:
                min_penalty = penalty
                best_match = PoseMatchResult(pose=reference_pose, deviations=deviations)

        if best_match is None:
            raise ValueError("No best match found")

        return best_match
