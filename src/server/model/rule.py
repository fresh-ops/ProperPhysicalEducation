from dataclasses import dataclass

from analyzer.pose.skeleton_transformer.skeleton import Angle


@dataclass
class Rule:
    pose_name: str
    feature: Angle
    operator: str
    value: float
    message: str
