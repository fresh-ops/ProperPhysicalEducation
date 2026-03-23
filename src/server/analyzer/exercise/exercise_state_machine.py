from analyzer.exercise.exercise_state import ExerciseState
from model.pose import Pose


class ExerciseStateMachine:
    def __init__(
        self, exercise_state: ExerciseState, poses: list[Pose], frame_tolerance: int
    ):
        self.poses = poses
        self.frame_tolerance = frame_tolerance
        self.exercise_state = exercise_state

    def update(self, matched_pose: Pose, current_pose: Pose) -> ExerciseState:
        current_reference_pose: Pose = self.poses[
            self.exercise_state.current_pose_index
        ]
        next_pose_index: int = (self.exercise_state.current_pose_index + 1) % len(
            self.poses
        )

        if matched_pose.id == current_reference_pose.id:
            self.exercise_state.frame_tolerance_counter += 1
            if self.exercise_state.frame_tolerance_counter >= self.frame_tolerance:
                if current_pose == current_reference_pose:
                    self.exercise_state.current_pose_index = next_pose_index
                self.exercise_state.frame_tolerance_counter = 0

        return self.exercise_state
