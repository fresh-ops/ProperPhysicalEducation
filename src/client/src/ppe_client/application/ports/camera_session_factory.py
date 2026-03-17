from typing import Protocol

from ppe_client.application.ports import CameraSession
from ppe_client.domain import CameraDescriptor


class CameraSessionFactory(Protocol):
    def create_for(self, camera: CameraDescriptor) -> CameraSession: ...
