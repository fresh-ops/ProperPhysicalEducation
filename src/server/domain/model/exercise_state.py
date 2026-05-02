from dataclasses import dataclass


@dataclass(frozen=True)
class ExerciseState:
    current_pose_index: int = 0
    frame_tolerance_counter: int = 0

    def increment_counter(self) -> "ExerciseState":
        return ExerciseState(
            current_pose_index=self.current_pose_index,
            frame_tolerance_counter=self.frame_tolerance_counter + 1,
        )

    def reset_counter(self) -> "ExerciseState":
        return ExerciseState(
            current_pose_index=self.current_pose_index, frame_tolerance_counter=0
        )

    def increment_pose_index(self, total_poses: int) -> "ExerciseState":
        return ExerciseState(
            current_pose_index=(self.current_pose_index + 1) % total_poses,
            frame_tolerance_counter=0,
        )
