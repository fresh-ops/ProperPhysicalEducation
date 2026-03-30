from dataclasses import dataclass

from domain.model.angle import Angle


@dataclass
class Rule:
    pose_id: str
    feature: Angle
    operator: str
    value: float
    message: str
