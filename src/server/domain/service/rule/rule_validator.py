from domain.service.rule.strategy.rule_validation_strategy import (
    RuleValidationStrategy,
)


class RuleValidator[R, T]:
    def __init__(
        self,
        rules: list[R],
        strategy: RuleValidationStrategy[R, T],
    ) -> None:
        self._rules = rules
        self._strategy = strategy

    def validate(self, data: T) -> list[R]:
        violations: list[R] = []
        for rule in self._rules:
            if self._strategy.validate(rule, data):
                violations.append(rule)
        return violations
