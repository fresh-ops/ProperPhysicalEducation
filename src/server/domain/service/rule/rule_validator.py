from typing import Any

from domain.model.rule import Rule
from domain.service.rule.strategy.rule_validation_strategy import (
    RuleValidationStrategy,
)


class RuleValidator:
    def __init__(
        self,
        rules: list[Rule],
        strategy: RuleValidationStrategy[Rule, Any],
    ) -> None:
        self._rules = rules
        self._strategy = strategy

    def validate(self, data: Any) -> list[Rule]:
        violations = []
        for rule in self._rules:
            if self._strategy.validate(rule, data):
                violations.append(rule)
        return violations
