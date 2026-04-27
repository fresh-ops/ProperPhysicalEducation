from typing import Tuple

from application.processor.process_context import ProcessContext
from application.processor.sensor_processor import SensorProcessor
from domain.model.emg import EmgReading
from domain.model.emg_rule import EmgRule
from domain.model.exercise_state import ExerciseState
from domain.model.feedback import Feedback
from domain.service.rule.rule_validator import RuleValidator


class EmgSensorProcessor(SensorProcessor):
    def __init__(self, rule_validator: RuleValidator[EmgRule, EmgReading]) -> None:
        self._rule_validator = rule_validator

    def process(
        self, context: ProcessContext, state: ExerciseState
    ) -> Tuple[list[Feedback], ExerciseState]:
        feedbacks = []
        for emg in context.emgs:
            violations = self._rule_validator.validate(emg)
            for violation in violations:
                feedbacks.append(
                    Feedback(
                        type="EMG",
                        message=f"EMG sensor {emg.sensor_id} is in {emg.zone.value} zone",
                    )
                )
        return feedbacks, state
