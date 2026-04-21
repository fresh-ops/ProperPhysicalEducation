from fastapi import APIRouter, HTTPException, status
from wireup import Injected

from application.service.get_exercises_use_case import GetExercisesUseCase
from domain.ports.errors import EntityNotFoundError

from presentation.schemas.exercises import ExerciseItem, ExercisesResponse

router = APIRouter(tags=["exercise"])


@router.get("/exercises", response_model=ExercisesResponse)
async def get_exercises(
    use_case: Injected[GetExercisesUseCase],
) -> ExercisesResponse:
    try:
        result = use_case.execute()
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ExercisesResponse(
        exercises=[
            ExerciseItem(exercise_id=item.exercise_id, name=item.name)
            for item in result.exercises
        ]
    )
