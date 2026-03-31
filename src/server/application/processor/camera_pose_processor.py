from typing import Tuple

from domain.model.exercise_state import ExerciseState
from domain.service.exercise_state_machine import ExerciseStateMachine
from application.processor.sensor_processor import SensorProcessor
from domain.model.feedback import Feedback, FeedbackType
from domain.model.pose import Pose
from domain.service.pose.pose_matcher.pose_matcher import PoseMatcher
from domain.service.rule.rule_validator import RuleValidator


class CameraPoseProcessor(SensorProcessor[Pose]):
    def __init__(
        self,
        poses: list[Pose],
        pose_matcher: PoseMatcher,
        rule_validator: RuleValidator,
        state_machine: ExerciseStateMachine,
    ) -> None:
        self._poses = poses
        self._pose_matcher = pose_matcher
        self._rule_validator = rule_validator
        self._state_machine = state_machine

    def process(
        self, data: Pose, state: ExerciseState
    ) -> Tuple[list[Feedback], ExerciseState]:
        match_result = self._pose_matcher.match(data)
        expected_pose = self._poses[state.current_pose_index]
        is_pose_matched = match_result.pose.id == expected_pose.id
        if not is_pose_matched:
            new_state = self._state_machine.update(
                state, is_pose_matched=False, is_pose_correct=False
            )
            return [
                Feedback(
                    type=FeedbackType.SYSTEM,
                    message=f"Сейчас нужно перейти в позу {expected_pose.name}",
                )
            ], new_state
        violations = self._rule_validator.validate(match_result)
        is_pose_correct = len(violations) == 0
        new_state = self._state_machine.update(
            state, is_pose_matched=is_pose_matched, is_pose_correct=is_pose_correct
        )
        feedbacks = [
            Feedback(type=FeedbackType.POSE, message=v.message) for v in violations
        ]
        if new_state.current_pose_index != state.current_pose_index:
            feedbacks.append(
                Feedback(
                    type=FeedbackType.SYSTEM,
                    message="Отлично! Переходим к следующему движению.",
                )
            )
        return feedbacks, new_state
