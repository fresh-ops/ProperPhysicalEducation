from application.dto.feedback import FeedbackItemDto, FeedbackResponseDto
from application.processor.process_context import ProcessContext
from application.processor.sensor_processor import SensorProcessorFactory
from domain.model.session_id import SessionId
from domain.ports.session_repository import SessionRepository


class EvaluateExerciseUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        processor_factories: list[SensorProcessorFactory],
    ):
        self._session_repository = session_repository
        self._processor_factories = processor_factories

    async def execute(
        self, session_id: SessionId, data: ProcessContext
    ) -> FeedbackResponseDto:
        session = await self._session_repository.get(session_id)
        feedbacks = []
        current_state = session.exercise_state
        for factory in self._processor_factories:
            processor = factory.create(session.exercise_id)
            feedback, current_state = processor.process(data, current_state)
            feedbacks.extend(feedback)

        session = session.update(new_state=current_state)

        await self._session_repository.update(session)

        return FeedbackResponseDto(
            feedbacks=[
                FeedbackItemDto(type=f.type, message=f.message) for f in feedbacks
            ]
        )
