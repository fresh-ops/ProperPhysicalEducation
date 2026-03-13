from PySide6 import QtCore

from ppe_client.application.ports import CameraGateway, PoseLandmarkerFactory
from ppe_client.domain import CameraDescriptor

from .pose_capture_worker import PoseCaptureWorker


class PoseCaptureSession(QtCore.QObject):
    """Own a single camera capture worker and its background Qt thread."""

    pose_ready = QtCore.Signal(object, object)
    finished = QtCore.Signal()
    failed_stopping = QtCore.Signal()

    _camera_info: CameraDescriptor
    _camera_service: CameraGateway
    _worker: PoseCaptureWorker | None
    _thread: QtCore.QThread | None
    _is_stopping_failed: bool

    def __init__(
        self,
        /,
        camera_info: CameraDescriptor,
        camera_service: CameraGateway,
        pose_landmarker_factory: PoseLandmarkerFactory,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self._camera_info = camera_info
        self._camera_service = camera_service
        self._pose_landmarker_factory = pose_landmarker_factory
        self._worker = None
        self._thread = None
        self._is_stopping_failed = False

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    @property
    def is_stopping_failed(self) -> bool:
        return self._is_stopping_failed

    @QtCore.Slot()
    def start(self) -> None:
        if self._thread is not None:
            return

        self._is_stopping_failed = False

        self._worker = PoseCaptureWorker(
            camera_info=self._camera_info,
            camera_service=self._camera_service,
            pose_landmarker_factory=self._pose_landmarker_factory,
        )
        self._thread = QtCore.QThread(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.pose_ready.connect(self.pose_ready)

        self._worker.finished.connect(self.finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.destroyed.connect(self._clear)

        self._thread.start()

    @QtCore.Slot()
    def stop(self) -> None:
        if self._thread is None or self._worker is None:
            return

        self._worker.stop()
        self._thread.quit()
        success = self._thread.wait(1_500)
        if not success:
            self._is_stopping_failed = True
            self.failed_stopping.emit()
        else:
            self._clear()

    @QtCore.Slot()
    def _clear(self) -> None:
        self._worker = None
        self._thread = None
        self._is_stopping_failed = False
