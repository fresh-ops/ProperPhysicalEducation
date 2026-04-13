from PySide6 import QtCore, QtGui

from ppe_client.adapters.cameras import FrameConverter
from ppe_client.adapters.poses import LandmarksDrawer
from ppe_client.application.cameras import CameraSessionService, Frame
from ppe_client.application.cameras.ports import CameraSession
from ppe_client.application.poses import Pose, PoseService
from ppe_client.domain import CameraDescriptor


class CameraCaptureViewModel(QtCore.QObject):
    """View model that controls camera capture lifecycle for preview UI.

    Signals:
        frame_ready: Emitted when a converted ``QPixmap`` frame is ready
            for rendering in the view.
    """

    frame_ready = QtCore.Signal(QtGui.QPixmap)

    _session_service: CameraSessionService
    _pose_service: PoseService
    _camera: CameraDescriptor
    _session: CameraSession | None

    def __init__(
        self,
        session_service: CameraSessionService,
        pose_service: PoseService,
        camera: CameraDescriptor,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize capture dependencies and optional initial camera state.

        Args:
            session_service (CameraSessionService): Shared capture
                sessions coordinator.
            pose_service (PoseService): Pose detecting service.
            camera_info (CameraDescriptor): Capturing camera.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership and signal lifecycle.
        """
        super().__init__(parent)
        self._session_service = session_service
        self._pose_service = pose_service
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
        self._session.attach(self._on_frame_ready)

    @QtCore.Slot()
    def stop_capture(self) -> None:
        """Stop active capture thread and release worker references."""
        if self._session is None:
            return

        self._session.detach(self._on_frame_ready)
        if self._camera is not None:
            self._session_service.disconnect(self._camera)
        self._session = None

    @QtCore.Slot(object)
    def _on_frame_ready(self, frame: Frame) -> None:
        if self._camera is None:
            return
        self._pose_service.detect(self._camera, frame, self._on_pose_ready)

    @QtCore.Slot(object, object)
    def _on_pose_ready(self, pose: Pose | None, frame: Frame) -> None:
        if pose is not None:
            frame = LandmarksDrawer().draw(pose, frame)
        pixmap = FrameConverter.to_pixel_map(frame)

        self.frame_ready.emit(pixmap)
