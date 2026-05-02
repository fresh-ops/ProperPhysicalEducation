from domain.model.pose_match_result import PoseMatchResult
from domain.model.pose_rule import OPERATORS, PoseRule
from domain.service.rule.strategy.rule_validation_strategy import (
    RuleValidationStrategy,
)


class PoseRuleStrategy(RuleValidationStrategy[PoseRule, PoseMatchResult]):
    def validate(self, rule: PoseRule, data: PoseMatchResult) -> bool:
        if data.pose.id != rule.id:
            return False
        angle_value = data.deviations.get(rule.feature, 0)
        if OPERATORS[rule.operator](angle_value, rule.value):
            return True
        return False
