from typing import Any

from PySide6 import QtCore


class SelectCameraViewModel(QtCore.QObject):
    """View model for loading and tracking camera selection.

    Signals:
        available_cameras_updated: Emitted with a full list of camera names
            whenever camera options are refreshed.
    """

    available_cameras_updated = QtCore.Signal(list)

    _selected_camera_index: int = 0
    _cameras_list: list[str]

    def __init__(self, parent: QtCore.QObject | None = None, **kwargs: Any) -> None:
        """Initialize view model state and optionally set parent for Qt ownership.

        Args:
            parent (QtCore.QObject | None): Optional parent QObject for ownership and
                signal propagation.
            **kwargs: Additional keyword arguments for QObject initialization.
        """
        super().__init__(parent, **kwargs)
        self._cameras_list = []

    def update_available_cameras(self) -> None:
        """Refresh available camera names and notify observers.

        Note:
            Current implementation uses mock values and should later be
            replaced with real camera discovery.
        """
        self._cameras_list = ["Camera 1", "Camera 2", "Camera 3"]
        self.available_cameras_updated.emit(self._cameras_list)

    def set_selected_camera_index(self, index: int) -> None:
        """Set currently selected camera index.

        Args:
            index (int): Zero-based index in the current camera list.
        """
        self._selected_camera_index = index

    def get_selected_camera(self) -> str:
        """Return selected camera name from the latest camera list.

        Returns:
            str: The name of the currently selected camera.
        """
        return self._cameras_list[self._selected_camera_index]
