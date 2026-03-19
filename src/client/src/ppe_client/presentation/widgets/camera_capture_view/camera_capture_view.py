from typing import override

from PySide6 import QtCore, QtGui, QtWidgets

from ppe_client.application.cameras import CameraSessionService
from ppe_client.domain import CameraDescriptor

from .camera_capture_view_model import CameraCaptureViewModel


class CameraCaptureView(QtWidgets.QWidget):
    """Widget for displaying a live preview from the selected camera.

    UI rendering responsibilities are kept in this view, while camera capture
    lifecycle is delegated to ``CameraCaptureViewModel``.
    """

    _vm: CameraCaptureViewModel

    def __init__(
        self,
        session: CameraSessionService,
        camera: CameraDescriptor | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """Initialize preview UI and bind it to the camera capture view model.

        Args:
            camera_service (CameraSessionService): Shared coordinator for camera
                capture sessions lifecycle.
            camera (CameraDescriptor | None): Optional camera used as initial
                capture source. If not provided, the first available camera is used.
            parent (QtWidgets.QWidget | None): Optional parent widget for Qt
                ownership.
        """
        super().__init__(parent)

        self._vm = CameraCaptureViewModel(
            session_service=session,
            camera=camera,
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

    @QtCore.Slot(QtGui.QPixmap)
    def _on_frame_ready(self, pixmap: QtGui.QPixmap) -> None:
        """Render the latest frame received from the view model.

        Args:
            pixmap (QtGui.QPixmap): Frame image from the camera.
        """
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

    def update_camera(self, camera: CameraDescriptor) -> None:
        """Switch preview to another camera.

        Args:
            camera (CameraDescriptor): Camera metadata for the new capture source.
        """
        self._vm.update_camera(camera)
        self._preview_label.setText("Select a camera to start capturing")
