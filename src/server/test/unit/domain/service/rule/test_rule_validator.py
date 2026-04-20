from unittest.mock import Mock, call

from domain.model.rule import Rule
from domain.service.rule.rule_validator import RuleValidator
from domain.service.rule.strategy.rule_validation_strategy import (
    RuleValidationStrategy,
)


def test_validate_returns_only_violated_rules_in_original_order() -> None:
    rules = [
        Rule(message="first"),
        Rule(message="second"),
        Rule(message="third"),
    ]
    strategy = Mock(spec=RuleValidationStrategy)
    strategy.validate.side_effect = [False, True, True]

    validator: RuleValidator[Rule, object] = RuleValidator(
        rules=rules, strategy=strategy
    )
    violations = validator.validate(data={"key": "value"})

    assert violations == [rules[1], rules[2]]


def test_validate_returns_empty_list_when_no_violations() -> None:
    rules = [Rule(message="first"), Rule(message="second")]
    strategy = Mock(spec=RuleValidationStrategy)
    strategy.validate.side_effect = [False, False]

    validator: RuleValidator[Rule, object] = RuleValidator(
        rules=rules, strategy=strategy
    )
    violations = validator.validate(data=123)

    assert violations == []


def test_validate_calls_strategy_for_each_rule_with_same_data() -> None:
    rules = [Rule(message="first"), Rule(message="second")]
    payload = object()
    strategy = Mock(spec=RuleValidationStrategy)
    strategy.validate.side_effect = [True, False]

    validator: RuleValidator[Rule, object] = RuleValidator(
        rules=rules, strategy=strategy
    )
    validator.validate(data=payload)

    strategy.validate.assert_has_calls(
        [call(rules[0], payload), call(rules[1], payload)]
    )
    assert strategy.validate.call_count == 2


def test_validate_does_not_call_strategy_when_rules_are_empty() -> None:
    strategy = Mock(spec=RuleValidationStrategy)

    validator: RuleValidator[Rule, object] = RuleValidator(rules=[], strategy=strategy)
    violations = validator.validate(data="anything")

    assert violations == []
    strategy.validate.assert_not_called()
