from typing import Protocol

from ppe_client.domain import CameraDescriptor

from ..pose import Pose


class PoseReciever(Protocol):
    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None: ...
