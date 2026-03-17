from typing import Protocol

from ppe_client.application.ports import CameraSession, CameraSessionFactory
from ppe_client.domain import CameraDescriptor


class CameraSessionStorage(Protocol):
    def acquire(
        self, camera: CameraDescriptor, session_factory: CameraSessionFactory
    ) -> CameraSession:
        """Get a session associated with the camera."""
        ...

    def release(self, camera: CameraDescriptor) -> None:
        """Release the session associated with the camera."""
        ...
