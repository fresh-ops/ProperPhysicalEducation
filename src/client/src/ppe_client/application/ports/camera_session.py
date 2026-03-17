from typing import Protocol

from ppe_client.application.cameras import Frame


class CameraSession(Protocol):
    def start(self) -> None:
        """Start capturing."""
        ...

    def stop(self) -> None:
        """Stop capturing."""
        ...

    def read(self) -> Frame | None:
        """Read a frame from the camera."""
