from typing import Any, override

from PySide6 import QtCore, QtWidgets

from src.poses.cameras import CameraService

from ...routing import Screen
from ...widgets.camera_capture_view import CameraCaptureView
from ...widgets.select_camera_dialog import SelectCameraDialog
from .cameras_payload import CamerasPayload
from .cameras_view_model import CamerasViewModel


class CamerasScreen(Screen[CamerasPayload]):
    _vm: CamerasViewModel
    _camera_service: CameraService

    def __init__(self, camera_service: CameraService, **kwargs: Any):
        super().__init__(**kwargs)

        self._vm = CamerasViewModel()

        self._camera_service = camera_service

        self._button = QtWidgets.QPushButton("Select Camera")
        self._button.clicked.connect(self._on_button_clicked)

        self._preview = CameraCaptureView(self._camera_service, None, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._preview)
        layout.addWidget(self._button)
        self.setLayout(layout)

    @override
    def on_enter(self, payload: CamerasPayload | None = None) -> None:
        self._vm.bind_model(payload)

    @QtCore.Slot()
    def _on_button_clicked(self) -> None:
        dialog = SelectCameraDialog(self._camera_service, parent=self)
        result = dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            selected_camera = dialog.get_selected_camera_info()
            self._preview.update_camera_info(selected_camera)
