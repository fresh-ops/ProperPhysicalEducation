from cv2 import VideoCapture
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo

from .errors import CameraNotFoundError, CameraServiceDoubleInstanceError


class CameraService:
    _instance: "CameraService | None" = None
    _cameras: list[CameraInfo]

    def __init__(self) -> None:
        if CameraService._instance is not None:
            raise CameraServiceDoubleInstanceError()
        self._cameras = []
        CameraService._instance = self

    @classmethod
    def get_instance(cls) -> "CameraService":
        """Returns the singleton instance of CameraService.

        Returns:
            CameraService: The singleton instance of CameraService.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_cameras(self) -> list[CameraInfo]:
        """Returns a list of available cameras."""
        if self._cameras == []:
            self._update_cameras()
        return self._cameras

    def get_camera_by(self, index: int) -> VideoCapture:
        """Returns a camera by its index.

        Args:
            index (int): The index of the camera to retrieve.
        Returns:
            VideoCapture: The camera object corresponding to the specified index.
        Raises:
            CameraNotFoundError: If the camera with the specified index is not found.
        """
        if self._cameras == []:
            self._update_cameras()
        if index < 0 or index >= len(self._cameras):
            raise CameraNotFoundError(index)

        return VideoCapture(index)

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
