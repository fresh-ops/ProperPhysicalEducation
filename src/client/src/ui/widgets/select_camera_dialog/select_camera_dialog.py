from typing import Any

from PySide6 import QtCore, QtWidgets

from .select_camera_view_model import SelectCameraViewModel


class SelectCameraDialog(QtWidgets.QDialog):
    """Dialog for choosing one camera from the available camera list.

    Camera discovery and selection state are managed via
    ``SelectCameraViewModel``.
    """

    _vm: SelectCameraViewModel

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: Any) -> None:
        """Initialize dialog widgets and connect them to the view model.

        Args:
            parent (QtWidgets.QWidget | None): Optional parent widget for Qt ownership
                and modality.
            **kwargs: Additional keyword arguments for Qt dialog initialization.
        """
        super().__init__(parent, **kwargs)
        self.setWindowTitle("Select Camera")

        self._vm = SelectCameraViewModel()
        self._vm.available_cameras_updated.connect(self._on_available_cameras_updated)

        layout = QtWidgets.QVBoxLayout()

        self._accept_button = QtWidgets.QPushButton("Accept")
        self._accept_button.clicked.connect(self.accept)
        self._cameras_options = QtWidgets.QComboBox(self)
        self._cameras_options.currentIndexChanged.connect(self._on_camera_selected)

        layout.addWidget(self._cameras_options)
        layout.addWidget(self._accept_button)
        self.setLayout(layout)

        self._vm.update_available_cameras()

    def get_selected_camera(self) -> str:
        """Return currently selected camera name.

        Returns:
            str: The name of the currently selected camera.
        """
        return self._vm.get_selected_camera()

    @QtCore.Slot(int)
    def _on_camera_selected(self, selected_index: int) -> None:
        """Handle combobox index changes and update view model state.

        Args:
            selected_index (int): Zero-based index selected in the camera combobox.
        """
        self._vm.set_selected_camera_index(selected_index)

    @QtCore.Slot(list)
    def _on_available_cameras_updated(self, cameras: list[str]) -> None:
        """Populate camera combobox when the view model updates its data.

        Args:
            cameras (list[str]): Human-readable camera names available for selection.
        """
        self._cameras_options.addItems(cameras)
