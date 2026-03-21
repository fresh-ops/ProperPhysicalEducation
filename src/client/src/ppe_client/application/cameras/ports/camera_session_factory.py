from typing import Protocol

from ppe_client.domain import CameraDescriptor

from .camera_session import CameraSession


class CameraSessionFactory(Protocol):
    def create_for(self, camera: CameraDescriptor) -> CameraSession: ...
