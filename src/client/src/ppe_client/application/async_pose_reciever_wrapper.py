from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from ppe_client.domain import CameraDescriptor

from .poses.pose import Pose

AsyncPoseCallback = Callable[
    [Pose, CameraDescriptor | None],
    Coroutine[Any, Any, None],
]


class AsyncPoseReceiverWrapper:
    """
    Обёртка, позволяющая использовать async callback
    там, где ожидается синхронный PoseReceiver.
    """

    def __init__(self, callback: AsyncPoseCallback) -> None:
        self._callback = callback

    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None:
        asyncio.create_task(self._callback(pose, camera))  # noqa: RUF006
