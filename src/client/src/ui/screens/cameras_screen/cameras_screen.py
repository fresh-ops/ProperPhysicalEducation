from typing import Any, override

from PySide6 import QtWidgets

from ...routing import Screen
from .cameras_payload import CamerasPayload
from .cameras_view_model import CamerasViewModel


class CamerasScreen(Screen[CamerasPayload]):
    _vm: CamerasViewModel

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        self._vm = CamerasViewModel()

        self._label = QtWidgets.QLabel("You are at cameras screen")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label)
        self.setLayout(layout)

    @override
    def on_enter(self, payload: CamerasPayload | None = None) -> None:
        self._vm.bind_model(payload)
