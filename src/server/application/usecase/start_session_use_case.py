import uuid

from application.dto.session import StartSessionResponseDto
from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.session import Session
from domain.model.session_id import SessionId
from domain.ports.errors import EntityNotFoundError
from domain.ports.exercise_repository import ExerciseRepository
from domain.ports.session_repository import SessionRepository


class StartSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        exercise_repository: ExerciseRepository,
    ):
        self.session_repository = session_repository
        self.exercise_repository = exercise_repository

    async def execute(self, exercise_id: ExerciseId) -> StartSessionResponseDto:
        try:
            self.exercise_repository.get_by_id(exercise_id)
        except EntityNotFoundError:
            raise EntityNotFoundError("exercise", exercise_id.id)
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=SessionId(session_id),
            exercise_id=exercise_id,
            exercise_state=ExerciseState(),
        )
        await self.session_repository.create(session)
        return StartSessionResponseDto(session_id=session_id)
