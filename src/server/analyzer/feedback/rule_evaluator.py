import operator

from model.pose import Pose
from model.rule import Rule

OPERATORS = {"<": operator.lt, ">": operator.gt}


class RuleEvaluator:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def evaluate(self, current_pose: Pose, expected_pose: Pose) -> list[str]:
        messages = []

        for rule in self.rules:
            if rule.pose_name != expected_pose.name:
                continue

            angle_value = current_pose.angles.get(rule.feature, 0)
            if OPERATORS[rule.operator](angle_value, rule.value):
                messages.append(rule.message)

        return messages
