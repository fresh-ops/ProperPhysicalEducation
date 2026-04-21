from application.processor.camera.camera_pose_processor import CameraPoseProcessor
from application.processor.sensor_processor import SensorProcessorFactory
from domain.model.exercise_id import ExerciseId
from domain.ports.exercise_repository import ExerciseRepository
from domain.ports.pose_repository import PoseRepository
from domain.service.exercise_state_machine import ExerciseStateMachine
from domain.service.pose.pose_matcher.pose_matcher import PoseMatcher
from domain.service.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)
from domain.service.rule.rule_validator import RuleValidator
from domain.service.rule.strategy.pose_rule_strategy import PoseRuleStrategy


class CameraPoseProcessorFactory(SensorProcessorFactory):
    def __init__(
        self,
        exercise_repository: ExerciseRepository,
        pose_repository: PoseRepository,
        pose_matcher_strategy: PoseMatcherStrategy,
        frame_tolerance: int,
    ):
        self._exercise_repository = exercise_repository
        self._pose_repository = pose_repository
        self._pose_matcher_strategy = pose_matcher_strategy
        self._frame_tolerance = frame_tolerance

    def create(self, exercise_id: ExerciseId) -> CameraPoseProcessor:
        exercise = self._exercise_repository.get_by_id(exercise_id)
        poses = [self._pose_repository.get_by_id(pid) for pid in exercise.poses]
        pose_matcher = PoseMatcher(
            reference_poses=poses, strategy=self._pose_matcher_strategy
        )
        rule_validator = RuleValidator(
            rules=exercise.pose_rules, strategy=PoseRuleStrategy()
        )
        state_machine = ExerciseStateMachine(len(poses), self._frame_tolerance)
        return CameraPoseProcessor(
            pose_matcher=pose_matcher,
            rule_validator=rule_validator,
            state_machine=state_machine,
        )
