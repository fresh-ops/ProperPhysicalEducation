from PySide6 import QtCore, QtWidgets

from ppe_client.domain import CameraDescriptor

from .select_camera_view_model import SelectCameraViewModel


class SelectCameraDialog(QtWidgets.QDialog):
    """Dialog for choosing one camera from the available camera list.

    Camera discovery and selection state are managed via
    ``SelectCameraViewModel``.
    """

    _view_model: SelectCameraViewModel

    def __init__(
        self,
        view_model: SelectCameraViewModel,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """Initialize dialog widgets and connect them to the view model.

        Args:
            view_model (SelectCameraViewModel): ViewModel to control this dialog
            parent (QtWidgets.QWidget | None): Optional parent widget for Qt ownership
                and modality.
        """
        super().__init__(parent)
        self.setWindowTitle("Select Camera")

        self._view_model = view_model
        self._view_model.setParent(self)
        self.on_create()

    def on_create(self) -> None:
        self._view_model.available_cameras_updated.connect(
            self._on_available_cameras_updated
        )

        layout = QtWidgets.QVBoxLayout()

        self._accept_button = QtWidgets.QPushButton("Accept")
        self._accept_button.clicked.connect(self.accept)
        self._cameras_options = QtWidgets.QComboBox(self)
        self._cameras_options.currentIndexChanged.connect(self._on_camera_selected)

        layout.addWidget(self._cameras_options)
        layout.addWidget(self._accept_button)
        self.setLayout(layout)

        self._view_model.update_available_cameras()

    def on_destroy(self) -> None:
        self._view_model.available_cameras_updated.disconnect(
            self._on_available_cameras_updated
        )
        self._cameras_options.currentIndexChanged.disconnect(self._on_camera_selected)

    def get_selected_camera_info(self) -> CameraDescriptor:
        """Return the information about the selected camera.

        Returns:
            CameraDescriptor: the selected camera information
        """
        return self._view_model.get_selected_camera_info()

    @QtCore.Slot(int)
    def _on_camera_selected(self, selected_index: int) -> None:
        """Handle combobox index changes and update view model state.

        Args:
            selected_index (int): Zero-based index selected in the camera combobox.
        """
        self._view_model.set_selected_camera_index(selected_index)

    @QtCore.Slot(list)
    def _on_available_cameras_updated(self, cameras: list[str]) -> None:
        """Populate camera combobox when the view model updates its data.

        Args:
            cameras (list[str]): Human-readable camera names available for selection.
        """
        self._cameras_options.clear()
        self._cameras_options.addItems(cameras)
