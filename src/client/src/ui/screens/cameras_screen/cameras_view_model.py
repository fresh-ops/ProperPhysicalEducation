from PySide6 import QtCore

from .cameras_payload import CamerasPayload


class CamerasViewModel(QtCore.QObject):
    def bind_model(self, payload: CamerasPayload | None = None) -> None:
        if payload is None:
            return
