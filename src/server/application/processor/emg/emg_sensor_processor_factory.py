from application.processor.emg.emg_sensor_processor import EmgSensorProcessor
from application.processor.sensor_processor import (
    SensorProcessor,
    SensorProcessorFactory,
)
from domain.model.emg import EmgReading
from domain.model.emg_rule import EmgRule
from domain.model.exercise_id import ExerciseId
from domain.service.rule.rule_validator import RuleValidator


class EmgSensorProcessorFactory(SensorProcessorFactory):
    def __init__(self, rule_validator: RuleValidator[EmgRule, EmgReading]) -> None:
        self._rule_validator = rule_validator

    def create(self, exercise_id: ExerciseId) -> SensorProcessor:
        return EmgSensorProcessor(rule_validator=self._rule_validator)
