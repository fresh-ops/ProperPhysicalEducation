from cv2 import VideoCapture
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo


class CameraService:
    _cameras: list[CameraInfo]

    def __init__(self) -> None:
        self._cameras = []

    def get_cameras(self) -> list[CameraInfo]:
        """Returns a list of available cameras."""
        if self._cameras == []:
            self._update_cameras()
        return self._cameras

    def get_camera_by(self, info: CameraInfo) -> VideoCapture:
        """Returns a camera by its information.

        Args:
            info (CameraInfo): The information about a camera to get. This information
                should be taken from this CameraService.
        Returns:
            VideoCapture: The camera object corresponding to the specified information.
        """
        return VideoCapture(info.index, info.backend)

    def _update_cameras(self) -> None:
        """Refresh the cached camera list.

        Only cameras that can be opened for video capture are kept.
        """
        self._cameras = []
        raw_cameras = enumerate_cameras()
        for camera in raw_cameras:
            capture = VideoCapture(camera.index, camera.backend)
            if capture.isOpened():
                self._cameras.append(camera)
            capture.release()
