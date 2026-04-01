import asyncio
import json
from collections.abc import Callable

import httpx
import websockets
from websockets.asyncio.client import ClientConnection

from ppe_client.application.poses import Pose
from ppe_client.domain import CameraDescriptor

from ..poses.pose_converter import PoseConverter
from .schemas import (
    ErrorResponse,
    ExerciseItem,
    ExerciseRequest,
    ExercisesResponse,
    FeedbackResponse,
    LandmarksRequest,
    SessionResponse,
)


class ExerciseSession:
    _SERVER = "172.20.10.2"
    _START_EXCERCISE_ENDPOINT = f"http://{_SERVER}:8000/start"
    _ANALYZE_ENDPOINT = f"ws://{_SERVER}:8000/analyze/"
    _EXERCISES_ENDPOINT = f"http://{_SERVER}:8000/exercises"
    _callback: Callable[[FeedbackResponse], None] | None = None

    def __init__(self) -> None:
        self.websocket: ClientConnection | None = None
        self._recv_lock = asyncio.Lock()

    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        loop.create_task(self.receive_feedbacks(PoseConverter.to_list(pose)))  # noqa: RUF006

    async def get_exercises(self) -> list[ExerciseItem]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self._EXERCISES_ENDPOINT)
            except httpx.ConnectTimeout:
                return []

            response.raise_for_status()
            data = response.json()
            return ExercisesResponse(**data).exercises

    async def start(
        self, exercise_id: int, callback: Callable[[FeedbackResponse], None]
    ) -> None:
        self._callback = callback
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._START_EXCERCISE_ENDPOINT}",
                json=ExerciseRequest(id=exercise_id).model_dump(),
            )
            response.raise_for_status()
            data = response.json()
            session_id = SessionResponse(**data).session_id
            await self.__connect(session_id)

    async def __connect(self, session_id: str) -> None:
        self.websocket = await websockets.connect(
            f"{self._ANALYZE_ENDPOINT}{session_id}"
        )

    async def receive_feedbacks(
        self, landmarks: list[list[float]]
    ) -> FeedbackResponse | ErrorResponse:
        if not self.websocket:
            raise RuntimeError("WebSocket connection not established")
        try:
            request = LandmarksRequest(landmarks=landmarks)
            await self.websocket.send(json.dumps(request.model_dump()))
            async with self._recv_lock:
                response = await self.websocket.recv()
            data = json.loads(response)
            if "error" in data:
                return ErrorResponse(**data)
            else:
                feedback = FeedbackResponse(**data)
                if self._callback is not None:
                    self._callback(feedback)
                return feedback
        except Exception:
            raise

    async def close(self) -> None:
        if self.websocket:
            await self.websocket.close()
