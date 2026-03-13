from cv2.typing import MatLike
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
from PySide6 import QtCore, QtGui

from ppe_client.application.capturing import (
    PoseCaptureOrchestrator,
    PoseCaptureSession,
)
from ppe_client.domain import CameraDescriptor
from ppe_client.visualization import draw_landmarks_on_image


class CameraCaptureViewModel(QtCore.QObject):
    """View model that controls camera capture lifecycle for preview UI.

    Signals:
        frame_ready: Emitted when a converted ``QImage`` frame is ready
            for rendering in the view.
    """

    frame_ready = QtCore.Signal(QtGui.QImage)

    _capture_orchestrator: PoseCaptureOrchestrator
    _camera_info: CameraDescriptor | None
    _active_session_camera_info: CameraDescriptor | None
    _capture_session: PoseCaptureSession | None

    def __init__(
        self,
        capture_orchestrator: PoseCaptureOrchestrator,
        camera_info: CameraDescriptor | None = None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize capture dependencies and optional initial camera state.

        Args:
            capture_orchestrator (PoseCaptureOrchestrator): Shared capture
                sessions coordinator.
            camera_info (CameraDescriptor | None): Optional camera selected initially.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership and signal lifecycle.
        """
        super().__init__(parent)
        self._capture_orchestrator = capture_orchestrator
        self._camera_info = camera_info
        self._active_session_camera_info = None
        self._capture_session = None

    @QtCore.Slot()
    def start_capture(self) -> None:
        """Start frame capture with selected camera if provided."""
        if self._camera_info is None or self._capture_session is not None:
            return

        self._capture_session = self._capture_orchestrator.connect_session(
            self._camera_info
        )
        self._active_session_camera_info = self._camera_info
        self._capture_session.finished.connect(self._unwire_session)
        self._capture_session.pose_ready.connect(self._draw_frame)

    @QtCore.Slot()
    def stop_capture(self) -> None:
        """Stop active capture thread and release worker references."""
        if self._capture_session is None or self._active_session_camera_info is None:
            return

        self._capture_orchestrator.disconnect_session(self._active_session_camera_info)
        self._unwire_session()

    def update_camera_info(self, camera_info: CameraDescriptor) -> None:
        """Replace current camera source and restart capture.

        Args:
            camera_info (CameraDescriptor): Camera metadata used to configure
                the worker capture source.
        """
        self._camera_info = camera_info
        self.stop_capture()
        self.start_capture()

    @QtCore.Slot()
    def _unwire_session(self) -> None:
        if self._capture_session is None:
            return

        self._capture_session.pose_ready.disconnect(self._draw_frame)

        self._capture_session.finished.disconnect(self._unwire_session)

        self._active_session_camera_info = None
        self._capture_session = None

    @QtCore.Slot(object, object)
    def _draw_frame(self, pose: PoseLandmarkerResult, frame: MatLike) -> None:
        marked_frame = draw_landmarks_on_image(frame, pose)
        height, width, channels = marked_frame.shape
        image = QtGui.QImage(
            marked_frame.data,
            width,
            height,
            channels * width,
            QtGui.QImage.Format.Format_BGR888,
        )
        self.frame_ready.emit(image)
