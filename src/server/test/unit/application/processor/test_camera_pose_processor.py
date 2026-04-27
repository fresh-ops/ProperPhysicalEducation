from types import SimpleNamespace
from unittest.mock import Mock, patch

from application.processor.camera.camera_pose_processor import CameraPoseProcessor
from application.processor.process_context import ProcessContext
from domain.model.exercise_state import ExerciseState
from domain.model.pose import Pose
from domain.model.pose_id import PoseId


def _build_processor(
    *,
    expected_pose_id: PoseId,
    matched_pose_id: PoseId,
    violations: list[SimpleNamespace],
    current_index: int,
    next_index: int,
) -> tuple[
    CameraPoseProcessor, SimpleNamespace, Mock, Mock, Mock, Pose, SimpleNamespace
]:
    exercise = SimpleNamespace(
        poses=[SimpleNamespace(id=expected_pose_id, name="Поза 1")],
        rules=[object()],
    )
    pose_matcher = Mock()
    pose_matcher.reference_poses = exercise.poses
    rule_validator = Mock()
    state_machine = Mock()

    current_state = ExerciseState(
        current_pose_index=current_index, frame_tolerance_counter=0
    )
    new_state = ExerciseState(current_pose_index=next_index, frame_tolerance_counter=0)

    matched_pose = SimpleNamespace(id=matched_pose_id)
    match_result = SimpleNamespace(pose=matched_pose)

    state_machine.state = current_state
    state_machine.update.return_value = new_state
    pose_matcher.match.return_value = match_result
    rule_validator.validate.return_value = violations

    processor = CameraPoseProcessor(
        pose_matcher=pose_matcher,
        rule_validator=rule_validator,
        state_machine=state_machine,
    )
    input_pose = Pose(
        id=PoseId("test_pose"),
        name="Test Pose",
        threshold=0.1,
        left_shoulder_angle=90.0,
        right_shoulder_angle=90.0,
        left_elbow_angle=90.0,
        right_elbow_angle=90.0,
        left_knee_angle=90.0,
        right_knee_angle=90.0,
        left_hip_angle=90.0,
        right_hip_angle=90.0,
    )

    return (
        processor,
        exercise,
        pose_matcher,
        rule_validator,
        state_machine,
        input_pose,
        match_result,
    )


def test_process_returns_no_feedback_when_pose_matched_and_no_violations() -> None:
    (
        processor,
        exercise,
        pose_matcher,
        rule_validator,
        state_machine,
        input_pose,
        match_result,
    ) = _build_processor(
        expected_pose_id=PoseId("pose_1"),
        matched_pose_id=PoseId("pose_1"),
        violations=[],
        current_index=0,
        next_index=0,
    )

    current_state = state_machine.state
    context = ProcessContext(pose=input_pose, emgs=[])
    feedbacks, _ = processor.process(context, current_state)

    assert feedbacks == []
    pose_matcher.match.assert_called_once_with(input_pose)
    rule_validator.validate.assert_called_once_with(match_result)
    state_machine.update.assert_called_once_with(
        current_state,
        is_pose_matched=True,
        is_pose_correct=True,
    )


def test_process_returns_violation_feedback_messages() -> None:
    violations = [
        SimpleNamespace(message="Подними левую руку выше"),
        SimpleNamespace(message="Выпрями спину"),
    ]
    processor, _, _, _, state_machine, input_pose, _ = _build_processor(
        expected_pose_id=PoseId("pose_1"),
        matched_pose_id=PoseId("pose_1"),
        violations=violations,
        current_index=0,
        next_index=0,
    )

    current_state = state_machine.state
    context = ProcessContext(pose=input_pose, emgs=[])

    with patch(
        "application.processor.camera.camera_pose_processor.Feedback",
        side_effect=lambda *, type, message: SimpleNamespace(
            type=type, message=message
        ),
    ):
        feedbacks, _ = processor.process(context, current_state)

    assert [feedback.message for feedback in feedbacks] == [
        "Подними левую руку выше",
        "Выпрями спину",
    ]
    state_machine.update.assert_called_once_with(
        current_state,
        is_pose_matched=True,
        is_pose_correct=False,
    )


def test_process_appends_transition_feedback_when_pose_index_changes() -> None:
    processor, _, _, _, state_machine, input_pose, _ = _build_processor(
        expected_pose_id=PoseId("pose_1"),
        matched_pose_id=PoseId("pose_1"),
        violations=[],
        current_index=0,
        next_index=1,
    )

    current_state = state_machine.state
    context = ProcessContext(pose=input_pose, emgs=[])

    with patch(
        "application.processor.camera.camera_pose_processor.Feedback",
        side_effect=lambda *, type, message: SimpleNamespace(
            type=type, message=message
        ),
    ):
        feedbacks, _ = processor.process(context, current_state)

    assert [feedback.message for feedback in feedbacks] == [
        "Отлично! Переходим к следующему движению.",
    ]
