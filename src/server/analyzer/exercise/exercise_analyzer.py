from analyzer.exercise.exercise_state_machine import ExerciseStateMachine
from analyzer.feedback.feedback_generator import FeedbackGenerator
from analyzer.pose.pose_matcher.pose_matcher import PoseMatcher
from model.pose import Pose
from model.exercise import Exercise


class ExerciseAnalyzer:
    def __init__(
        self,
        exercise: Exercise,
        pose_matcher: PoseMatcher,
        exercise_state_machine: ExerciseStateMachine,
        feedback_generator: FeedbackGenerator,
    ):
        self.poses = exercise.poses
        self.pose_matcher = pose_matcher
        self.exercise_state_machine = exercise_state_machine
        self.feedback_generator = feedback_generator

    def analyze(self, current_pose: Pose) -> list[str]:
        matched_pose = self.pose_matcher.match(current_pose)
        exercise_state = self.exercise_state_machine.update(matched_pose.pose)
        expected_pose = self.poses[exercise_state.current_pose_index]
        feedbacks = self.feedback_generator.generate(
            matched_pose, current_pose, expected_pose
        )
        return feedbacks
