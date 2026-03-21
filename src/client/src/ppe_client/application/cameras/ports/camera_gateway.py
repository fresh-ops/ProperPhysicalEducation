from typing import Protocol

from cv2.typing import MatLike

from ppe_client.domain import CameraDescriptor


class CameraCapture(Protocol):
    """Minimal camera capture contract used by application workers."""

    def is_opened(self) -> bool: ...

    def read_frame(self) -> tuple[bool, MatLike]: ...

    def release(self) -> None: ...


class CameraGateway(Protocol):
    """Port for camera operations required by application use cases."""

    def get_cameras(self) -> list[CameraDescriptor]:
        """Return available camera descriptors."""
        ...

    def get_camera_by(self, info: CameraDescriptor) -> CameraCapture:
        """Open camera capture object for a descriptor."""
        ...
