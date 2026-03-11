import time

import mediapipe as mp
from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore, QtGui

from src.poses.cameras.camera_service import CameraService
from src.poses.model import create_video_pose_landmarker
from src.poses.visualize import draw_landmarks_on_image


class CameraCaptureWorker(QtCore.QObject):
    """Background worker that reads frames from OpenCV camera capture.

    Signals:
        frame_ready: Emitted with a ``QImage`` for each successfully read frame.
        finished: Emitted when capture loop exits or camera cannot be opened.
    """

    frame_ready = QtCore.Signal(QtGui.QImage)
    finished = QtCore.Signal()

    def __init__(
        self,
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
        self._running = True

    @QtCore.Slot()
    def run(self) -> None:
        """Run continuous capture loop and emit converted Qt frames."""
        capture = self._camera_service.get_camera_by(self._camera_info)
        if not capture.isOpened():
            self.finished.emit()
            return

        pose_landmarker = create_video_pose_landmarker()

        while self._running:
            success, cv_image = capture.read()
            if not success:
                continue

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_image)
            timestamp_ms = int(time.monotonic() * 1_000)
            pose = pose_landmarker.detect_for_video(mp_image, timestamp_ms)
            marked_frame = draw_landmarks_on_image(cv_image, pose)

            h, w, ch = marked_frame.shape
            qimg = QtGui.QImage(
                marked_frame.data,
                w,
                h,
                ch * w,
                QtGui.QImage.Format.Format_BGR888,
            )
            self.frame_ready.emit(qimg.copy())

        capture.release()
        self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        """Request capture loop termination on next iteration."""
        self._running = False
