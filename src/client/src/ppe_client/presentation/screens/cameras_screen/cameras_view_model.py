from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore

from ppe_client.poses.cameras import CameraKey, camera_key

from .cameras_payload import CamerasPayload


class CamerasViewModel(QtCore.QObject):
    cameras_changed = QtCore.Signal(list)

    _cameras_by_key: dict[CameraKey, CameraInfo]

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._cameras_by_key = {}

    def bind_model(self, payload: CamerasPayload | None = None) -> None:
        if payload is None:
            return

    def add_camera(self, camera_info: CameraInfo) -> bool:
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

    def get_cameras(self) -> list[CameraInfo]:
        return list(self._cameras_by_key.values())

    def camera_key(self, camera_info: CameraInfo) -> CameraKey:
        return camera_key(camera_info)
