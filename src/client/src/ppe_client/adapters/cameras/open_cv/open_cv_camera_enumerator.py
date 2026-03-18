from cv2 import VideoCapture
from cv2_enumerate_cameras import enumerate_cameras

from ppe_client.domain import CameraDescriptor


class OpenCVCameraEnumerator:
    _cameras: list[CameraDescriptor]

    def __init__(self) -> None:
        self._cameras = []

    def get_cameras(self) -> list[CameraDescriptor]:
        if self._cameras == []:
            self._update_cameras()
        return self._cameras

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
