from typing import Any, override

from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore, QtGui, QtWidgets

from ppe_client.poses.cameras import CameraService
from ppe_client.poses.capturing import PoseCaptureOrchestrator

from .camera_capture_view_model import CameraCaptureViewModel


class CameraCaptureView(QtWidgets.QWidget):
    """Widget for displaying a live preview from the selected camera.

    UI rendering responsibilities are kept in this view, while camera capture
    lifecycle is delegated to ``CameraCaptureViewModel``.
    """

    _vm: CameraCaptureViewModel

    def __init__(
        self,
        camera_service: CameraService,
        capture_orchestrator: PoseCaptureOrchestrator,
        camera_info: CameraInfo | None = None,
        parent: QtWidgets.QWidget | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize preview UI and bind it to the camera capture view model.

        Args:
            camera_service (CameraService): Service for retrieving cameras data.
            capture_orchestrator (PoseCaptureOrchestrator): Shared coordinator
                for camera capture sessions lifecycle.
            camera_info (CameraInfo | None): Optional camera used as initial
                capture source. If not provided, the first available camera is used.
            parent (QtWidgets.QWidget | None): Optional parent widget for Qt
                ownership.
            **kwargs: Additional keyword arguments for QWidget initialization.
        """
        super().__init__(parent, **kwargs)

        self._vm = CameraCaptureViewModel(
            camera_service=camera_service,
            capture_orchestrator=capture_orchestrator,
            camera_info=camera_info,
            parent=self,
        )
        self._vm.frame_ready.connect(self._on_frame_ready)
        self._vm.start_capture()

        layout = QtWidgets.QVBoxLayout(self)
        self._preview_label = QtWidgets.QLabel(
            parent=self, text="Select a camera to start capturing"
        )
        self._preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._preview_label)
        self.setLayout(layout)

    @QtCore.Slot(QtGui.QImage)
    def _on_frame_ready(self, qimg: QtGui.QImage) -> None:
        """Render the latest frame received from the view model.

        Args:
            qimg (QtGui.QImage): Frame image prepared by camera worker.
        """
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self._preview_label.setPixmap(pixmap)

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Stop capture before widget destruction.

        Args:
            event (QtGui.QCloseEvent): Qt close event propagated to base class.
        """
        self.stop_capture()
        super().closeEvent(event)

    def start_capture(self) -> None:
        """Ensure camera capture is running for this preview."""
        self._vm.start_capture()

    def stop_capture(self) -> None:
        """Ensure camera capture is stopped for this preview."""
        self._vm.stop_capture()

    def update_camera_info(self, camera_info: CameraInfo) -> None:
        """Switch preview to another camera.

        Args:
            camera_info (CameraInfo): Camera metadata for the new capture source.
        """
        self._vm.update_camera_info(camera_info)
        self._preview_label.setText("Select a camera to start capturing")
