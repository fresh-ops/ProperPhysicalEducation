from typing import override

from PySide6 import QtCore, QtGui, QtWidgets

from .camera_capture_view_model import CameraCaptureViewModel


class CameraCaptureWidget(QtWidgets.QWidget):
    """Widget for displaying a live preview from the selected camera.

    UI rendering responsibilities are kept in this view, while camera capture
    lifecycle is delegated to ``CameraCaptureViewModel``.
    """

    _view_model: CameraCaptureViewModel
    _preview_label: QtWidgets.QLabel

    def __init__(
        self,
        view_model: CameraCaptureViewModel,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """Initialize preview UI and bind it to the camera capture view model.

        Args:
            view_model (CameraCaptureViewModel): Controlling view model.
            parent (QtWidgets.QWidget | None): Optional parent widget for Qt
                ownership.
        """
        super().__init__(parent)

        self._view_model = view_model
        self.on_create()

    def on_create(self) -> None:
        """Set up layout and signals."""
        self._view_model.frame_ready.connect(self._on_frame_ready)

        self._preview_label = QtWidgets.QLabel(
            parent=self, text="Select a camera to start capturing"
        )
        self._preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        root = QtWidgets.QVBoxLayout(self)
        root.addWidget(self._preview_label)
        self.setLayout(root)

        self.start_capture()

    def on_destroy(self) -> None:
        self.stop_capture()
        self._view_model.frame_ready.disconnect(self._on_frame_ready)

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
        self.on_destroy()
        super().closeEvent(event)

    def start_capture(self) -> None:
        """Ensure camera capture is running for this preview."""
        self._view_model.start_capture()

    def stop_capture(self) -> None:
        """Ensure camera capture is stopped for this preview."""
        self._view_model.stop_capture()
