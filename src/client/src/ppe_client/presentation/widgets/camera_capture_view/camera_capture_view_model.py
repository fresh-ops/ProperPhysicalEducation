from PySide6 import QtCore, QtGui

from ppe_client.adapters.cameras import FrameConverter
from ppe_client.application.cameras import CameraSessionService, Frame
from ppe_client.application.ports import CameraSession
from ppe_client.domain import CameraDescriptor


class CameraCaptureViewModel(QtCore.QObject):
    """View model that controls camera capture lifecycle for preview UI.

    Signals:
        frame_ready: Emitted when a converted ``QPixmap`` frame is ready
            for rendering in the view.
    """

    frame_ready = QtCore.Signal(QtGui.QPixmap)

    _session_service: CameraSessionService
    _camera: CameraDescriptor | None
    _session: CameraSession | None

    def __init__(
        self,
        session_service: CameraSessionService,
        camera: CameraDescriptor | None = None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize capture dependencies and optional initial camera state.

        Args:
            session_service (CameraSessionService): Shared capture
                sessions coordinator.
            camera_info (CameraDescriptor | None): Optional camera selected initially.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership and signal lifecycle.
        """
        super().__init__(parent)
        self._session_service = session_service
        self._camera = camera
        self._session = None

    @QtCore.Slot()
    def start_capture(self) -> None:
        """Start frame capture with selected camera if provided."""
        if self._camera is None:
            return

        if self._session is not None:
            self.stop_capture()

        self._session = self._session_service.connect(self._camera)
        self._session.attach(self._draw_frame)

    @QtCore.Slot()
    def stop_capture(self) -> None:
        """Stop active capture thread and release worker references."""
        if self._session is None:
            return

        self._session.detach(self._draw_frame)
        if self._camera is not None:
            self._session_service.disconnect(self._camera)
        self._session = None

    def update_camera(self, camera: CameraDescriptor) -> None:
        """Replace current camera source and restart capture.

        Args:
            camera (CameraDescriptor): Camera metadata used to configure
                the worker capture source.
        """
        self.stop_capture()
        self._camera = camera
        self.start_capture()

    @QtCore.Slot(object)
    def _draw_frame(self, frame: Frame) -> None:
        pixmap = FrameConverter.to_pixel_map(frame)

        self.frame_ready.emit(pixmap)
