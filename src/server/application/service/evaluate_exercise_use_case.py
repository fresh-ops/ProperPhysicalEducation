from application.dto.feedback import FeedbackItemDto, FeedbackResponseDto
from application.dto.process import ProcessRequestDto
from application.mapper.process_context_mapper import ProcessContextMapper
from application.processor.sensor_processor import SensorProcessor
from domain.model.session_id import SessionId
from domain.ports.session_repository import SessionRepository


class EvaluateExerciseUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        processors: list[SensorProcessor],
        context_mapper: ProcessContextMapper,
    ):
        self._session_repository = session_repository
        self._processors = processors
        self._context_mapper = context_mapper

    async def execute(
        self, session_id: SessionId, data: ProcessRequestDto
    ) -> FeedbackResponseDto:
        session = await self._session_repository.get(session_id)
        context = self._context_mapper.to_context(data)

        feedbacks = []
        current_state = session.exercise_state
        for processor in self._processors:
            feedback, current_state = processor.process(context, current_state)
            feedbacks.extend(feedback)

        session = session.update(new_state=current_state)

        await self._session_repository.update(session)

        return FeedbackResponseDto(
            feedbacks=[
                FeedbackItemDto(type=f.type, message=f.message) for f in feedbacks
            ]
        )
