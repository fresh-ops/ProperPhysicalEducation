from analyzer.exercise.exercise_state_machine import ExerciseStateMachine
from analyzer.pose.pose_matcher.pose_matcher import PoseMatcher
from model.pose import Pose
from model.exercise import Exercise


class ExerciseAnalyzer:
    def __init__(
        self,
        exercise: Exercise,
        pose_matcher: PoseMatcher,
        exercise_state_machine: ExerciseStateMachine,
    ):
        self.poses = exercise.poses
        self.pose_detector = pose_matcher
        self.exercise_state_machine = exercise_state_machine

    def analyze(self, current_pose: Pose) -> int:
        matched_pose = self.pose_detector.match(current_pose)
        exercise_state = self.exercise_state_machine.update(matched_pose.pose)
        return exercise_state.current_pose_index
