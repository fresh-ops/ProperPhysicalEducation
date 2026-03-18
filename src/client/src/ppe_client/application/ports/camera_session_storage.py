from typing import Protocol

from ppe_client.domain import CameraDescriptor

from .camera_session import CameraSession
from .camera_session_factory import CameraSessionFactory


class CameraSessionStorage(Protocol):
    def acquire(
        self, camera: CameraDescriptor, session_factory: CameraSessionFactory
    ) -> CameraSession:
        """Get a session associated with the camera."""
        ...

    def release(self, camera: CameraDescriptor) -> None:
        """Release the session associated with the camera."""
        ...
