from cv2 import VideoCapture
from cv2.typing import MatLike
from cv2_enumerate_cameras import enumerate_cameras

from ppe_client.domain import CameraDescriptor


class OpenCvCameraCapture:
    """Adapter over cv2.VideoCapture exposing an application-friendly contract."""

    def __init__(self, capture: VideoCapture) -> None:
        self._capture = capture

    def is_opened(self) -> bool:
        return self._capture.isOpened()

    def read_frame(self) -> tuple[bool, MatLike]:
        return self._capture.read()

    def release(self) -> None:
        self._capture.release()


class CameraService:
    _cameras: list[CameraDescriptor]

    def __init__(self) -> None:
        self._cameras = []

    def get_cameras(self) -> list[CameraDescriptor]:
        """Return a list of available cameras."""
        if self._cameras == []:
            self._update_cameras()
        return self._cameras

    def get_camera_by(self, info: CameraDescriptor) -> OpenCvCameraCapture:
        """Return an opened camera capture by camera descriptor."""
        return OpenCvCameraCapture(VideoCapture(info.index, info.backend))

    def _update_cameras(self) -> None:
        self._cameras = []
        raw_cameras = enumerate_cameras()
        for camera in raw_cameras:
            capture = VideoCapture(camera.index, camera.backend)
            if capture.isOpened():
                self._cameras.append(
                    CameraDescriptor(
                        name=camera.name,
                        index=camera.index,
                        backend=camera.backend,
                    )
                )
            capture.release()
