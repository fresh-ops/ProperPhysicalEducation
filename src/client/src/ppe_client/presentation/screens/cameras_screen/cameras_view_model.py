from PySide6 import QtCore

from ppe_client.domain import CameraDescriptor, CameraKey, camera_key

from .cameras_payload import CamerasPayload


class CamerasViewModel(QtCore.QObject):
    cameras_changed = QtCore.Signal(list)

    _cameras_by_key: dict[CameraKey, CameraDescriptor]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._cameras_by_key = {}

    def bind_model(self, payload: CamerasPayload | None = None) -> None:
        if payload is None:
            return

    def add_camera(self, camera_info: CameraDescriptor) -> bool:
        key = camera_key(camera_info)
        if key in self._cameras_by_key:
            return False

        self._cameras_by_key[key] = camera_info
        self.cameras_changed.emit(self.get_cameras())
        return True

    def clear_cameras(self) -> None:
        if not self._cameras_by_key:
            return

        self._cameras_by_key.clear()
        self.cameras_changed.emit([])

    def has_cameras(self) -> bool:
        return bool(self._cameras_by_key)

    def get_cameras(self) -> list[CameraDescriptor]:
        return list(self._cameras_by_key.values())

    def camera_key(self, camera_info: CameraDescriptor) -> CameraKey:
        return camera_key(camera_info)
