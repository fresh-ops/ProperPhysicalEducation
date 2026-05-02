from domain.model.exercise_id import ExerciseId
from presentation.schemas.session import StartSessionRequest


def map_to_exercise_id(request: StartSessionRequest) -> ExerciseId:
    return ExerciseId(request.exercise_id)
