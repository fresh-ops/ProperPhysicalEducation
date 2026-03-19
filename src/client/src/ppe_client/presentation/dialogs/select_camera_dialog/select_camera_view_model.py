from PySide6 import QtCore

from ppe_client.application.ports import CameraEnumerator
from ppe_client.domain import CameraDescriptor


class SelectCameraViewModel(QtCore.QObject):
    """View model for loading and tracking camera selection.

    Signals:
        available_cameras_updated: Emitted with a full list of camera names
            whenever camera options are refreshed.
    """

    available_cameras_updated = QtCore.Signal(list)

    _selected_camera_index: int = 0
    _cameras_list: list[CameraDescriptor]
    _camera_enumerator: CameraEnumerator

    def __init__(
        self,
        camera_enumerator: CameraEnumerator,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Initialize view model state and optionally set parent for Qt ownership.

        Args:
            camera_enumerator (CameraEnumerator): Port for retrieving camera data.
            parent (QtCore.QObject | None): Optional parent QObject for ownership and
                signal propagation.
        """
        super().__init__(parent)
        self._cameras_list = []
        self._camera_enumerator = camera_enumerator

    def update_available_cameras(self) -> None:
        """Refresh available camera names and notify observers.

        Note:
            Current implementation uses mock values and should later be
            replaced with real camera discovery.
        """
        self._cameras_list = self._camera_enumerator.get_cameras()
        names = [camera.name for camera in self._cameras_list]
        self.available_cameras_updated.emit(names)

    def set_selected_camera_index(self, index: int) -> None:
        """Set currently selected camera index.

        Args:
            index (int): Zero-based index in the current camera list.
        """
        self._selected_camera_index = index

    def get_selected_camera_info(self) -> CameraDescriptor:
        """Return the inforamation about the selected camera.

        Returns:
            CameraDescriptor: the selected camera infromation.
        """
        return self._cameras_list[self._selected_camera_index]
