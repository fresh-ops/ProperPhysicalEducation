import time

from PySide6 import QtCore

from ppe_client.application.ports import CameraGateway, PoseLandmarkerFactory
from ppe_client.domain import CameraDescriptor


class PoseCaptureWorker(QtCore.QObject):
    """Background worker that reads frames from camera and detects human pose."""

    pose_ready = QtCore.Signal(object, object)
    finished = QtCore.Signal()

    def __init__(
        self,
        /,
        camera_info: CameraDescriptor,
        camera_service: CameraGateway,
        pose_landmarker_factory: PoseLandmarkerFactory,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._camera_info = camera_info
        self._camera_service = camera_service
        self._pose_landmarker_factory = pose_landmarker_factory
        self._running = False

    @QtCore.Slot()
    def run(self) -> None:
        self._running = True
        capture = self._camera_service.get_camera_by(self._camera_info)
        if not capture.is_opened():
            capture.release()
            self.finished.emit()
            return

        pose_landmarker = self._pose_landmarker_factory()

        try:
            while self._running:
                success, cv_image = capture.read_frame()
                if not success:
                    continue

                timestamp_ms = int(time.monotonic() * 1_000)
                pose = pose_landmarker.detect_for_video_frame(cv_image, timestamp_ms)
                self.pose_ready.emit(pose, cv_image)
        finally:
            capture.release()
            pose_landmarker.close()
            self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        self._running = False
