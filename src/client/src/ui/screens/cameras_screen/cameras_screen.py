from typing import Any, override

from PySide6 import QtCore, QtWidgets

from ...routing import Screen
from ...widgets.select_camera_dialog import SelectCameraDialog
from .cameras_payload import CamerasPayload
from .cameras_view_model import CamerasViewModel


class CamerasScreen(Screen[CamerasPayload]):
    _vm: CamerasViewModel

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        self._vm = CamerasViewModel()

        self._label = QtWidgets.QLabel("You are at cameras screen")
        self._button = QtWidgets.QPushButton("Select Camera")
        self._button.clicked.connect(self._on_button_clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._button)
        self.setLayout(layout)

    @override
    def on_enter(self, payload: CamerasPayload | None = None) -> None:
        self._vm.bind_model(payload)

    @QtCore.Slot()
    def _on_button_clicked(self) -> None:
        dialog = SelectCameraDialog(parent=self)
        result = dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            selected_camera = dialog.get_selected_camera()
            print(selected_camera)
