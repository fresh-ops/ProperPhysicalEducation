from typing import Any

from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore, QtGui

from src.poses.cameras import CameraCaptureWorker, CameraService


class CameraCaptureViewModel(QtCore.QObject):
    """View model that controls camera capture lifecycle for preview UI.

    Signals:
        frame_ready: Emitted when a converted ``QImage`` frame is ready
            for rendering in the view.
    """

    frame_ready = QtCore.Signal(QtGui.QImage)
    _capture_worker: CameraCaptureWorker | None = None
    _capture_thread: QtCore.QThread | None = None

    def __init__(
        self,
        camera_service: CameraService,
        camera_info: CameraInfo | None = None,
        parent: QtCore.QObject | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize capture dependencies and optional initial camera state.

        Args:
            camera_service (CameraService): Camera service used to resolve
                available devices and default camera.
            camera_info (CameraInfo | None): Optional camera selected initially.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership and signal lifecycle.
            **kwargs: Additional keyword arguments for QObject initialization.
        """
        super().__init__(parent, **kwargs)
        self._camera_service = camera_service
        self._camera_info = camera_info
        self._capture_thread = None
        self._capture_worker = None

    def start_capture(self) -> None:
        """Start frame capture with selected or default camera.

        Note:
            If there are no available cameras, method exits without starting
            the worker thread.
        """
        camera_info = self._camera_info or self._get_default_camera()
        if camera_info is None:
            return

        self._camera_info = camera_info
        self._start_worker_with(camera_info)

    def stop_capture(self) -> None:
        """Stop active capture thread and release worker references."""
        if self._capture_thread is None or self._capture_worker is None:
            return

        if self._capture_worker and not self._capture_thread.isFinished():
            self._capture_worker.stop()
            self._capture_thread.quit()
            self._capture_thread.wait(1500)

        self._clear_thread()

    def update_camera_info(self, camera_info: CameraInfo) -> None:
        """Replace current camera source and restart capture.

        Args:
            camera_info (CameraInfo): Camera metadata used to configure
                the worker capture source.
        """
        self._camera_info = camera_info
        self.stop_capture()
        self.start_capture()

    def _get_default_camera(self) -> CameraInfo | None:
        """Return first available camera or ``None`` if list is empty.

        Returns:
            CameraInfo | None: First discovered camera, if present.
        """
        cameras = self._camera_service.get_cameras()
        if not cameras:
            return None
        return cameras[0]

    def _start_worker_with(self, camera_info: CameraInfo) -> None:
        """Create and start worker thread configured for a camera.

        Args:
            camera_info (CameraInfo): Camera metadata used by worker capture loop.
        """
        if self._capture_thread is not None or self._capture_worker is not None:
            self.stop_capture()

        self._capture_thread = QtCore.QThread(self)
        self._capture_worker = CameraCaptureWorker(camera_info)
        self._capture_worker.moveToThread(self._capture_thread)

        self._capture_thread.started.connect(self._capture_worker.run)
        self._capture_worker.frame_ready.connect(self.frame_ready)
        self._capture_worker.finished.connect(self._capture_thread.quit)
        self._capture_worker.finished.connect(self._capture_worker.deleteLater)
        self._capture_thread.finished.connect(self._capture_thread.deleteLater)
        self._capture_thread.destroyed.connect(self._clear_thread)
        self._capture_thread.start()

    def _clear_thread(self) -> None:
        """Clear internal thread and worker references after capture shutdown.

        Note:
            This method only resets view model state. It does not stop or join
            a running thread and should be called after stop/finish handling.
        """
        self._capture_worker = None
        self._capture_thread = None
