from dataclasses import dataclass

from analyzer.pose.skeleton_transformer.skeleton import Angle
from model.pose import Pose


@dataclass
class PoseMatchResult:
    pose: Pose
    deviations: dict[Angle, float]
