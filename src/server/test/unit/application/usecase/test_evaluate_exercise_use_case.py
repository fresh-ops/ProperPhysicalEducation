from unittest.mock import AsyncMock, Mock

import pytest

from application.processor.process_context import ProcessContext
from application.usecase.evaluate_exercise_use_case import EvaluateExerciseUseCase
from application.dto.feedback import FeedbackItemDto
from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.feedback import Feedback, FeedbackType
from domain.model.session import Session
from domain.model.session_id import SessionId
from domain.ports.session_repository import SessionRepository
from domain.service.pose.skeleton_transformer import landmarks_to_pose


def _landmarks_32() -> list[list[float]]:
    return [[float(i), float(i + 1), float(i + 2)] for i in range(32)]


@pytest.mark.asyncio
async def test_execute_processes_processors_in_order_and_persists_final_state() -> None:
    session = Session(
        session_id=SessionId("session-1"),
        exercise_id=ExerciseId("exercise-1"),
        exercise_state=ExerciseState(current_pose_index=0, frame_tolerance_counter=0),
    )
    session_repository = Mock(spec=SessionRepository)
    session_repository.get = AsyncMock(return_value=session)
    session_repository.update = AsyncMock(return_value=session)

    first_state = ExerciseState(current_pose_index=1, frame_tolerance_counter=0)
    second_state = ExerciseState(current_pose_index=2, frame_tolerance_counter=0)
    first_processor = Mock()
    first_processor.process.return_value = (
        [Feedback(type=FeedbackType.POSE, message="first")],
        first_state,
    )
    second_processor = Mock()
    second_processor.process.return_value = (
        [Feedback(type=FeedbackType.SYSTEM, message="second")],
        second_state,
    )
    first_factory = Mock()
    first_factory.create.return_value = first_processor
    second_factory = Mock()
    second_factory.create.return_value = second_processor

    use_case = EvaluateExerciseUseCase(
        session_repository=session_repository,
        processor_factories=[first_factory, second_factory],
    )
    request = ProcessContext(pose=landmarks_to_pose(_landmarks_32()), emgs=[])

    response = await use_case.execute(session.session_id, request)

    session_repository.get.assert_awaited_once_with(session.session_id)
    first_call_args = first_processor.process.call_args.args
    second_call_args = second_processor.process.call_args.args
    assert first_call_args[0] is request
    assert second_call_args[0] is request
    assert first_call_args[1] == session.exercise_state
    assert second_call_args[1] == first_state
    session_repository.update.assert_awaited_once()

    updated_session = session_repository.update.await_args.args[0]
    assert updated_session.exercise_state == second_state
    assert response.feedbacks == [
        FeedbackItemDto(type=FeedbackType.POSE.value, message="first"),
        FeedbackItemDto(type=FeedbackType.SYSTEM.value, message="second"),
    ]


@pytest.mark.asyncio
async def test_execute_handles_empty_processor_list() -> None:
    session = Session(
        session_id=SessionId("session-2"),
        exercise_id=ExerciseId("exercise-2"),
        exercise_state=ExerciseState(current_pose_index=3, frame_tolerance_counter=1),
    )
    session_repository = Mock(spec=SessionRepository)
    session_repository.get = AsyncMock(return_value=session)
    session_repository.update = AsyncMock(return_value=session)

    use_case = EvaluateExerciseUseCase(
        session_repository=session_repository,
        processor_factories=[],
    )

    response = await use_case.execute(
        session.session_id,
        ProcessContext(pose=landmarks_to_pose(_landmarks_32()), emgs=[]),
    )

    session_repository.get.assert_awaited_once_with(session.session_id)
    session_repository.update.assert_awaited_once_with(session)
    assert response.feedbacks == []
