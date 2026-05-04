from domain.model.emg import EmgReading
from domain.model.emg_rule import EmgRule
from domain.service.rule.strategy.rule_validation_strategy import RuleValidationStrategy


class EmgRuleStrategy(RuleValidationStrategy[EmgRule, EmgReading]):
    def validate(self, rule: EmgRule, data: EmgReading) -> bool:
        return data.zone == rule.target_zone
