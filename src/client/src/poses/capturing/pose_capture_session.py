from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore

from src.poses.cameras import CameraService

from .pose_capture_worker import PoseCaptureWorker


class PoseCaptureSession(QtCore.QObject):
    """Own a single camera capture worker and its background Qt thread.

    This session encapsulates thread lifecycle for one camera source and
    exposes a small state API for orchestrators.

    Signals:
        pose_ready (Signal): Forwarded from worker when pose result and frame
            are available.
        finished (Signal): Emitted when worker exits its capture loop.
        failed_stopping (Signal): Emitted when ``stop`` times out waiting for
            thread termination.
    """

    pose_ready = QtCore.Signal(object, object)
    finished = QtCore.Signal()
    failed_stopping = QtCore.Signal()

    _camera_info: CameraInfo
    _camera_service: CameraService
    _worker: PoseCaptureWorker | None
    _thread: QtCore.QThread | None
    _is_stopping_failed: bool

    def __init__(
        self,
        /,
        camera_info: CameraInfo,
        camera_service: CameraService,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize a capture session bound to one camera descriptor.

        Args:
            camera_info (CameraInfo): Selected camera metadata used to open
                capture.
            camera_service (CameraService): Service used by worker to create
                camera capture.
            parent (QtCore.QObject | None): Optional Qt parent for ownership
                and lifecycle management.
        """
        super().__init__(parent=parent)

        self._camera_info = camera_info
        self._camera_service = camera_service
        self._worker = None
        self._thread = None
        self._is_stopping_failed = False

    @property
    def is_running(self) -> bool:
        """Return whether the session currently has an active capture thread.

        Returns:
            bool: ``True`` when capture thread is allocated and not cleared.
        """
        return self._thread is not None

    @property
    def is_stopping_failed(self) -> bool:
        """Return whether the latest stop attempt timed out.

        This flag is reset on successful start and clear.

        Returns:
            bool: ``True`` if the previous ``stop`` timed out.
        """
        return self._is_stopping_failed

    @QtCore.Slot()
    def start(self) -> None:
        """Start worker and thread if session is not already running.

        Repeated calls while running are ignored.
        """
        if self._thread is not None:
            return

        self._is_stopping_failed = False

        self._worker = PoseCaptureWorker(
            camera_info=self._camera_info,
            camera_service=self._camera_service,
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
        """Request cooperative worker shutdown and wait for thread exit.

        If shutdown does not complete within 1500 ms, ``failed_stopping`` is
        emitted and internal references are intentionally preserved so caller
        can decide recovery strategy.
        """
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
        """Reset worker/thread references and failure flag after shutdown."""
        self._worker = None
        self._thread = None
        self._is_stopping_failed = False
