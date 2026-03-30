from dataclasses import dataclass

from domain.model.angle import Angle
from domain.model.pose_id import PoseId


@dataclass
class Rule:
    pose_id: PoseId
    feature: Angle
    operator: str
    value: float
    message: str
