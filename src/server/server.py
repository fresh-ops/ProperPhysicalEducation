import asyncio
import uuid
import logging
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from analyzer.exercise.exercise_analyzer import ExerciseAnalyzer
from analyzer.factory.exercise_analyzer_factory import ExerciseAnalyzerFactory
from loader.exercise_loader import ExerciseLoader
from loader.pose_loader import PoseLoader
from schemas.error import ErrorResponse
from schemas.exercise import ExerciseRequest
from schemas.exercises import ExercisesResponse, ExerciseItem
from analyzer.pose.skeleton_transformer.skeleton_transformer import landmarks_to_pose
from schemas.landmarks import LandmarksRequest
from schemas.feedback import FeedbackResponse, FeedbackItem
from schemas.session import SessionResponse
from config import settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = FastAPI()
logger = logging.getLogger(__name__)

sessions: dict[str, ExerciseAnalyzer] = {}
exercise_loader = ExerciseLoader(
    PoseLoader(settings.pose_data_path), settings.exercise_data_path
)
analyzer_factory = ExerciseAnalyzerFactory(exercise_loader)


@app.post("/start", response_model=SessionResponse)
def start(request: ExerciseRequest) -> SessionResponse:
    session_id = str(uuid.uuid4())
    analyzer = analyzer_factory.create(request.id)
    sessions[session_id] = analyzer
    return SessionResponse(session_id=session_id)


@app.get("/exercises", response_model=ExercisesResponse)
def exercises() -> ExercisesResponse:
    exercises_list = exercise_loader.get_exercises()
    exercise_items = [ExerciseItem(id=ex.id, name=ex.name) for ex in exercises_list]
    return ExercisesResponse(exercises=exercise_items)


@app.websocket("/analyze/{session_id}")
async def analyze(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    analyzer = sessions.get(session_id)
    if analyzer is None:
        await websocket.send_json(
            ErrorResponse(error="Invalid session Id").model_dump()
        )
        await websocket.close(code=1008)
        return

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
                request = LandmarksRequest(**data)
            except ValidationError as e:
                logger.warning("Validation error for session %s: %s", session_id, e)
                await websocket.send_json(
                    ErrorResponse(error="Invalid landmarks format").model_dump()
                )
                continue

            feedbacks = await asyncio.to_thread(
                analyzer.analyze, landmarks_to_pose(request.landmarks)
            )
            feedback_items = [FeedbackItem(message=feedback) for feedback in feedbacks]

            await websocket.send_json(
                FeedbackResponse(feedbacks=feedback_items).model_dump()
            )

    except WebSocketDisconnect:
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
    finally:
        sessions.pop(session_id, None)
