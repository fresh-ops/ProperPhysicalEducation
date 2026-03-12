import time

import mediapipe as mp
from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore

from ppe_client.poses.cameras.camera_service import CameraService
from ppe_client.poses.model import create_video_pose_landmarker


class PoseCaptureWorker(QtCore.QObject):
    """Background worker that reads frames from camera and detects the human pose.

    Signals:
        pose_ready: Emitted with a ``PoseLandmarkerResult`` and ``MatLike`` for
            each successfully detected pose.
        finished: Emitted when capture loop exits or camera cannot be opened.
    """

    pose_ready = QtCore.Signal(object, object)
    finished = QtCore.Signal()

    def __init__(
        self,
        /,
        camera_info: CameraInfo,
        camera_service: CameraService,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize worker state for a specific camera.

        Args:
            camera_info (CameraInfo): Camera metadata containing index and backend
                used to open the capture device.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership.
        """
        super().__init__(parent)
        self._camera_info = camera_info
        self._camera_service = camera_service
        self._running = False

    @QtCore.Slot()
    def run(self) -> None:
        """Run continuous capture loop and emit converted Qt frames."""
        self._running = True
        capture = self._camera_service.get_camera_by(self._camera_info)
        if not capture.isOpened():
            capture.release()
            self.finished.emit()
            return

        pose_landmarker = create_video_pose_landmarker()

        try:
            while self._running:
                success, cv_image = capture.read()
                if not success:
                    continue

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_image)
                timestamp_ms = int(time.monotonic() * 1_000)
                try:
                    pose = pose_landmarker.detect_for_video(mp_image, timestamp_ms)
                except RuntimeError:
                    # Runtime can already be shutting down while worker exits.
                    break
                self.pose_ready.emit(pose, cv_image)
        finally:
            capture.release()
            pose_landmarker.close()
            self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        """Request capture loop termination on next iteration."""
        self._running = False
