from typing import Any

from application.dto.feedback import FeedbackItemDto, FeedbackResponseDto
from application.dto.process import ProcessRequestDto
from application.processor.sensor_processor import SensorProcessor
from domain.model.session_id import SessionId
from domain.ports.errors import EntityNotFoundError
from domain.ports.session_repository import SessionRepository


class EvaluateExerciseUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        processors: list[SensorProcessor[Any]],
    ):
        self._session_repository = session_repository
        self._processors = processors

    def execute(
        self, session_id: SessionId, data: ProcessRequestDto
    ) -> FeedbackResponseDto:
        session = self._session_repository.get(session_id)
        if session is None:
            raise EntityNotFoundError(f"Session with id {session_id} not found")
        feedbacks = []
        for processor in self._processors:
            feedback, new_state = processor.process(data, session.exercise_state)
            session.update(new_state=new_state)
            feedbacks.extend(feedback)

        return FeedbackResponseDto(
            feedbacks=[
                FeedbackItemDto(type=f.type, message=f.message) for f in feedbacks
            ]
        )
