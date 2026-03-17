from typing import Protocol

from ppe_client.domain import CameraDescriptor


class CameraEnumerator(Protocol):
    def get_cameras(self) -> list[CameraDescriptor]:
        """Return a list of available cameras."""
        ...
