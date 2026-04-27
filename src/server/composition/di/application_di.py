from typing import Annotated

from wireup import Inject, injectable


from application.processor.camera.camera_pose_processor_factory import (
    CameraPoseProcessorFactory,
)
from application.processor.emg.emg_sensor_processor_factory import (
    EmgSensorProcessorFactory,
)
from domain.model.emg import EmgReading
from domain.model.emg_rule import EmgRule
from domain.model.zone import Zone
from domain.ports.exercise_repository import ExerciseRepository
from domain.ports.pose_repository import PoseRepository
from domain.service.pose.pose_matcher.strategy.penalty_strategy import PenaltyStrategy
from domain.service.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)

from application.processor.sensor_processor import SensorProcessorFactory
from domain.service.rule.rule_validator import RuleValidator
from domain.service.rule.strategy.emg_rule_strategy import EmgRuleStrategy


@injectable
def make_camera_pose_processor_factory(
    exercise_repository: ExerciseRepository,
    pose_repository: PoseRepository,
    pose_matcher_strategy: PoseMatcherStrategy,
    frame_tolerance: int,
) -> CameraPoseProcessorFactory:
    return CameraPoseProcessorFactory(
        exercise_repository=exercise_repository,
        pose_repository=pose_repository,
        pose_matcher_strategy=pose_matcher_strategy,
        frame_tolerance=frame_tolerance,
    )


@injectable
def make_emg_sensor_processor_factory(
    rule_validator: RuleValidator[EmgRule, EmgReading],
) -> EmgSensorProcessorFactory:
    return EmgSensorProcessorFactory(rule_validator=rule_validator)


@injectable
def make_rule_validator(
    emg_rules: list[EmgRule],
    emg_rule_strategy: EmgRuleStrategy,
) -> RuleValidator[EmgRule, EmgReading]:
    return RuleValidator(rules=emg_rules, strategy=emg_rule_strategy)


@injectable
def make_emg_rules() -> list[EmgRule]:
    return [EmgRule(target_zone=Zone.RED)]


@injectable
def make_emg_rule_strategy() -> EmgRuleStrategy:
    return EmgRuleStrategy()


@injectable
def make_frame_tolerance(
    frame_tolerance: Annotated[int, Inject(config="frame_tolerance")],
) -> int:
    return frame_tolerance


@injectable
def make_pose_matcher_strategy() -> PoseMatcherStrategy:
    return PenaltyStrategy()


@injectable
def make_processor_factories(
    camera_pose_processor_factory: CameraPoseProcessorFactory,
    emg_sensor_processor_factory: EmgSensorProcessorFactory,
) -> list[SensorProcessorFactory]:
    return [
        camera_pose_processor_factory,
        emg_sensor_processor_factory,
    ]
