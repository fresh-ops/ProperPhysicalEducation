import asyncio
import json
from collections.abc import Callable

import httpx
import websockets
from websockets.asyncio.client import ClientConnection

from ppe_client.application.poses import Pose
from ppe_client.domain import CameraDescriptor

from ..poses.pose_converter import PoseConverter
from .network_settings import NetworkSettings
from .schemas import (
    ErrorResponse,
    ExerciseItem,
    ExercisesResponse,
    FeedbackResponse,
    ProcessRequest,
    StartSessionRequest,
    StartSessionResponse,
)


class ExerciseSession:
    def __init__(self, settings: NetworkSettings | None = None) -> None:
        self.settings = settings or NetworkSettings()
        self.websocket: ClientConnection | None = None
        self._recv_lock = asyncio.Lock()
        self._callback: Callable[[FeedbackResponse], None] | None = None

    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        loop.create_task(self.receive_feedbacks(PoseConverter.to_list(pose)))  # noqa: RUF006

    async def get_exercises(
        self, callback: Callable[[list[ExerciseItem]], None]
    ) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.settings.exercises_url)
            response.raise_for_status()
            data = response.json()
            callback(ExercisesResponse(**data).exercises)

    async def start(
        self, exercise_id: str, callback: Callable[[FeedbackResponse], None]
    ) -> None:
        self._callback = callback
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.start_url,
                json=StartSessionRequest(exercise_id=exercise_id).model_dump(),
            )
            response.raise_for_status()
            data = response.json()
            session_id = StartSessionResponse(**data).session_id
            await self.__connect(session_id)

    async def __connect(self, session_id: str) -> None:
        self.websocket = await websockets.connect(self.settings.analyze_url(session_id))

    async def receive_feedbacks(
        self, landmarks: list[list[float]]
    ) -> FeedbackResponse | ErrorResponse:
        if not self.websocket:
            raise RuntimeError("WebSocket connection not established")
        try:
            request = ProcessRequest(landmarks=landmarks)
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
