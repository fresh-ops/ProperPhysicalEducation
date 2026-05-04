import asyncio
import json
from collections.abc import Callable

import httpx
import websockets
from websockets.asyncio.client import ClientConnection

from ppe_client.adapters.network.mappers import map_to_list, map_to_schema
from ppe_client.application.feedback import Feedback
from ppe_client.application.process_data import ProcessData
from ppe_client.domain import CameraDescriptor

from .network_settings import NetworkSettings
from .schemas import (
    ExerciseItem,
    ExercisesResponse,
    FeedbackResponse,
    StartSessionRequest,
    StartSessionResponse,
)


class ExerciseSession:
    def __init__(self, settings: NetworkSettings | None = None) -> None:
        self.settings = settings or NetworkSettings()
        self.websocket: ClientConnection | None = None
        self._recv_lock = asyncio.Lock()
        self._callback: Callable[[list[Feedback]], None] | None = None

    def recieve(
        self, data: ProcessData, camera: CameraDescriptor | None = None
    ) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        loop.create_task(self.receive_feedbacks(data))  # noqa: RUF006

    async def get_exercises(self) -> list[ExerciseItem]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.settings.exercises_url)
            response.raise_for_status()
            data = response.json()
            return ExercisesResponse(**data).exercises

    async def start(
        self, exercise_id: str, callback: Callable[[list[Feedback]], None]
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

    async def receive_feedbacks(self, data: ProcessData) -> list[Feedback]:
        if not self.websocket:
            raise RuntimeError("WebSocket connection not established")

        request = map_to_schema(data)

        async with self._recv_lock:
            await self.websocket.send(json.dumps(request.model_dump()))
            response = await self.websocket.recv()

        payload = json.loads(response)

        if "error" in payload:
            raise RuntimeError(payload["error"])

        return map_to_list(FeedbackResponse(**payload))

    async def close(self) -> None:
        if self.websocket:
            await self.websocket.close()
