from domain.model.exercise_state import ExerciseState


class ExerciseStateMachine:
    def __init__(self, total_poses: int, frame_tolerance: int):
        self._total_poses = total_poses
        self._frame_tolerance = frame_tolerance

    def update(
        self, state: ExerciseState, is_pose_matched: bool, is_pose_correct: bool
    ) -> ExerciseState:
        if not is_pose_matched:
            return state.reset_counter()

        new_state = state.increment_counter()

        if (
            new_state.frame_tolerance_counter >= self._frame_tolerance
            and is_pose_correct
        ):
            return state.increment_pose_index(self._total_poses)

        return new_state
