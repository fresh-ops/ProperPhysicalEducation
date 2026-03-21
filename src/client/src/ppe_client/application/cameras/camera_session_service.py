from ppe_client.domain import CameraDescriptor

from .ports import (
    CameraSession,
    CameraSessionFactory,
    CameraSessionStorage,
)


class CameraSessionService:
    """Service that handles camera session connections."""

    _storage: CameraSessionStorage
    _factory: CameraSessionFactory

    def __init__(
        self, storage: CameraSessionStorage, factory: CameraSessionFactory
    ) -> None:
        self._storage = storage
        self._factory = factory

    def connect(self, camera: CameraDescriptor) -> CameraSession:
        """Connect to the session associated with the camera."""
        return self._storage.acquire(camera, self._factory)

    def disconnect(self, camera: CameraDescriptor) -> None:
        """Disconnect from the session associated with the camera."""
        self._storage.release(camera)
