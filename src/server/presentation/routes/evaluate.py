import asyncio
from venv import logger

from fastapi import APIRouter, WebSocket
from pydantic_core import ValidationError
from wireup import Injected

from application.dto.process import ProcessRequestDto
from application.usecase.evaluate_exercise_use_case import EvaluateExerciseUseCase
from domain.model.session_id import SessionId

from presentation.schemas.error import ErrorResponse
from presentation.schemas.feedback import FeedbackItem, FeedbackResponse
from config import settings
from presentation.schemas.process import ProcessRequest

router = APIRouter(tags=["evaluate"])


@router.websocket("/analyze/{session_id}")
async def analyze(
    websocket: WebSocket, session_id: str, use_case: Injected[EvaluateExerciseUseCase]
) -> None:
    await websocket.accept()
    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(), timeout=settings.session_timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.info("Session %s timed out", session_id)
                await websocket.close(code=1001)
                break
            try:
                request = ProcessRequest(**data)
            except ValidationError as e:
                logger.warning("Validation error for session %s: %s", session_id, e)
                await websocket.send_json(
                    ErrorResponse(error="Invalid landmarks format").model_dump()
                )
                continue

            feedback_response = await use_case.execute(
                session_id=SessionId(session_id),
                data=ProcessRequestDto(request.landmarks),
            )
            feedback_items = [
                FeedbackItem(message=feedback.message, type=feedback.type)
                for feedback in feedback_response.feedbacks
            ]

            await websocket.send_json(
                FeedbackResponse(feedbacks=feedback_items).model_dump()
            )

        logger.info("WebSocket disconnected for session %s", session_id)
    except (TypeError, ValueError, KeyError) as exc:
        logger.warning("Invalid payload for session %s: %s", session_id, exc)
        await websocket.send_json(
            ErrorResponse(error="Invalid payload format").model_dump()
        )
    except Exception:
        logger.exception("Unexpected error while analyzing session %s", session_id)
        try:
            await websocket.send_json(
                ErrorResponse(error="Internal server error").model_dump()
            )
        except Exception:
            pass
        await websocket.close(code=1011)
