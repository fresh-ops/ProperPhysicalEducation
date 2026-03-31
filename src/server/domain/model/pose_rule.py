from dataclasses import dataclass
import operator

from domain.model.angle import Angle
from domain.model.pose_id import PoseId
from domain.model.rule import Rule


OPERATORS = {"<": operator.lt, ">": operator.gt}


@dataclass
class PoseRule(Rule):
    id: PoseId
    feature: Angle
    operator: str
    value: float
    message: str
