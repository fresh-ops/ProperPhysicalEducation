from fastapi import APIRouter, HTTPException, status
from wireup import Injected

from application.usecase.start_session_use_case import StartSessionUseCase
from domain.ports.errors import EntityNotFoundError

from presentation.schemas.session import StartSessionRequest, StartSessionResponse
from presentation.mapper.session_request_mapper import map_to_exercise_id

router = APIRouter(tags=["session"])


@router.post("/start", response_model=StartSessionResponse)
async def start(
    request: StartSessionRequest,
    use_case: Injected[StartSessionUseCase],
) -> StartSessionResponse:
    try:
        result = await use_case.execute(map_to_exercise_id(request))
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return StartSessionResponse(session_id=result.session_id)
