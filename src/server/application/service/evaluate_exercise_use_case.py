from typing import Any

from application.dto.feedback import FeedbackItemDto, FeedbackResponseDto
from application.dto.process import ProcessRequestDto
from application.processor.sensor_processor import SensorProcessor
from domain.model.session_id import SessionId
from domain.ports.session_repository import SessionRepository


class EvaluateExerciseUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        processors: list[SensorProcessor[Any]],
    ):
        self._session_repository = session_repository
        self._processors = processors

    async def execute(
        self, session_id: SessionId, data: ProcessRequestDto
    ) -> FeedbackResponseDto:
        session = await self._session_repository.get(session_id)
        feedbacks = []
        for processor in self._processors:
            feedback, new_state = processor.process(data, session.exercise_state)
            session = session.update(new_state=new_state)
            feedbacks.extend(feedback)

        await self._session_repository.update(session)

        return FeedbackResponseDto(
            feedbacks=[
                FeedbackItemDto(type=f.type, message=f.message) for f in feedbacks
            ]
        )
