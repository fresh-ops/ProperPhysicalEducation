from domain.model.exercise_state import ExerciseState
from domain.service.exercise_state_machine import ExerciseStateMachine


def test_update_resets_counter_when_pose_not_matched() -> None:
    machine = ExerciseStateMachine(
        total_poses=3,
        frame_tolerance=2,
    )

    new_state = machine.update(
        state=ExerciseState(current_pose_index=1, frame_tolerance_counter=3),
        is_pose_matched=False,
        is_pose_correct=True,
    )

    assert new_state == ExerciseState(current_pose_index=1, frame_tolerance_counter=0)


def test_update_increments_counter_when_pose_matched_but_not_yet_tolerated() -> None:
    machine = ExerciseStateMachine(
        total_poses=3,
        frame_tolerance=2,
    )

    new_state = machine.update(
        state=ExerciseState(current_pose_index=0, frame_tolerance_counter=0),
        is_pose_matched=True,
        is_pose_correct=True,
    )

    assert new_state == ExerciseState(current_pose_index=0, frame_tolerance_counter=1)


def test_update_moves_to_next_pose_when_tolerance_reached_and_pose_correct() -> None:
    machine = ExerciseStateMachine(
        total_poses=3,
        frame_tolerance=2,
    )

    new_state = machine.update(
        state=ExerciseState(current_pose_index=0, frame_tolerance_counter=1),
        is_pose_matched=True,
        is_pose_correct=True,
    )

    assert new_state == ExerciseState(current_pose_index=1, frame_tolerance_counter=0)


def test_update_does_not_move_to_next_pose_when_pose_incorrect() -> None:
    machine = ExerciseStateMachine(
        total_poses=3,
        frame_tolerance=2,
    )

    new_state = machine.update(
        state=ExerciseState(current_pose_index=0, frame_tolerance_counter=1),
        is_pose_matched=True,
        is_pose_correct=False,
    )

    assert new_state == ExerciseState(current_pose_index=0, frame_tolerance_counter=2)


def test_update_wraps_pose_index_after_last_pose() -> None:
    machine = ExerciseStateMachine(
        total_poses=3,
        frame_tolerance=2,
    )

    new_state = machine.update(
        state=ExerciseState(current_pose_index=2, frame_tolerance_counter=1),
        is_pose_matched=True,
        is_pose_correct=True,
    )

    assert new_state == ExerciseState(current_pose_index=0, frame_tolerance_counter=0)
