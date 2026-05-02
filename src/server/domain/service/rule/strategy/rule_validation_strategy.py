from abc import ABC, abstractmethod


class RuleValidationStrategy[R, T](ABC):
    @abstractmethod
    def validate(self, rule: R, data: T) -> bool:
        pass
