from dataclasses import dataclass

from domain.model.angle import Angle
from domain.model.pose import Pose


@dataclass
class PoseMatchResult:
    pose: Pose
    deviations: dict[Angle, float]
