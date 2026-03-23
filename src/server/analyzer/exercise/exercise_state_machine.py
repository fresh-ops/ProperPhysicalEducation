from analyzer.exercise.exercise_state import ExerciseState
from model.pose import Pose


class ExerciseStateMachine:
    def __init__(self, poses: list[Pose], frame_tolerance: int):
        self.poses = poses
        self.frame_tolerance = frame_tolerance
        self.exercise_state = ExerciseState()

    def update(self, matched_pose: Pose) -> ExerciseState:
        current_reference_pose: Pose = self.poses[
            self.exercise_state.current_pose_index
        ]
        next_pose_index: int = (self.exercise_state.current_pose_index + 1) % len(
            self.poses
        )

        if matched_pose.id == current_reference_pose.id:
            self.exercise_state.hold_frame_count += 1
            if self.exercise_state.hold_frame_count >= self.frame_tolerance:
                self.exercise_state.current_pose_index = next_pose_index
                self.exercise_state.hold_frame_count = 0
        else:
            self.exercise_state.hold_frame_count = 0

        return self.exercise_state
