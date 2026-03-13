from typing import override

from PySide6 import QtCore, QtWidgets

from ppe_client.application.capturing import PoseCaptureOrchestrator
from ppe_client.application.ports import CameraGateway
from ppe_client.domain import CameraDescriptor, CameraKey
from ppe_client.presentation.dialogs.select_camera_dialog import SelectCameraDialog
from ppe_client.presentation.routing import Screen
from ppe_client.presentation.widgets.camera_capture_view import CameraCaptureView

from .cameras_payload import CamerasPayload
from .cameras_view_model import CamerasViewModel


class CamerasScreen(Screen[CamerasPayload]):
    _vm: CamerasViewModel
    _camera_gateway: CameraGateway
    _capture_orchestrator: PoseCaptureOrchestrator

    def __init__(
        self,
        camera_gateway: CameraGateway,
        capture_orchestrator: PoseCaptureOrchestrator,
    ) -> None:
        super().__init__()

        self._vm = CamerasViewModel()
        self._vm.cameras_changed.connect(self._on_cameras_changed)

        self._camera_gateway = camera_gateway
        self._capture_orchestrator = capture_orchestrator

        self._grid_columns = 2
        self._previews_by_camera: dict[CameraKey, CameraCaptureView] = {}

        self._add_camera_button = QtWidgets.QPushButton("Add Camera")
        self._add_camera_button.clicked.connect(self._on_button_clicked)

        self._clear_button = QtWidgets.QPushButton("Clear")
        self._clear_button.clicked.connect(self._clear_previews)

        self._empty_state = QtWidgets.QLabel("No cameras selected")
        self._empty_state.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._grid = QtWidgets.QGridLayout()
        self._grid.setSpacing(8)

        previews_container = QtWidgets.QWidget(self)
        previews_container.setLayout(self._grid)

        self._scroll = QtWidgets.QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(previews_container)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self._add_camera_button)
        controls.addWidget(self._clear_button)
        controls.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._scroll)
        layout.addWidget(self._empty_state)
        layout.addLayout(controls)
        self.setLayout(layout)

        self._sync_empty_state_visibility()

    @override
    def on_enter(self, payload: CamerasPayload | None = None) -> None:
        self._vm.bind_model(payload)
        for preview in self._previews_by_camera.values():
            preview.start_capture()

    @override
    def on_leave(self) -> None:
        for preview in self._previews_by_camera.values():
            preview.stop_capture()

    @QtCore.Slot()
    def _on_button_clicked(self) -> None:
        dialog = SelectCameraDialog(self._camera_gateway, parent=self)
        result = dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            selected_camera = dialog.get_selected_camera_info()
            was_added = self._vm.add_camera(selected_camera)
            if not was_added:
                QtWidgets.QMessageBox.information(
                    self,
                    "Camera Already Added",
                    "Selected camera is already displayed.",
                )

    @QtCore.Slot(list)
    def _on_cameras_changed(self, cameras: list[CameraDescriptor]) -> None:
        keyed = [(self._vm.camera_key(c), c) for c in cameras]
        active_keys = {key for key, _ in keyed}

        for key in list(self._previews_by_camera):
            if key not in active_keys:
                preview = self._previews_by_camera.pop(key)
                preview.close()
                preview.deleteLater()

        for key, camera in keyed:
            if key not in self._previews_by_camera:
                self._previews_by_camera[key] = self._create_preview(camera)

        self._rebuild_grid(cameras)
        self._sync_empty_state_visibility()

    def _create_preview(self, camera_info: CameraDescriptor) -> CameraCaptureView:
        preview = CameraCaptureView(
            capture_orchestrator=self._capture_orchestrator,
            camera_info=camera_info,
            parent=self,
        )
        preview.setMinimumHeight(240)
        preview.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        return preview

    @QtCore.Slot()
    def _clear_previews(self) -> None:
        self._vm.clear_cameras()

    def _rebuild_grid(self, cameras: list[CameraDescriptor]) -> None:
        while self._grid.count() > 0:
            item = self._grid.takeAt(0)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        for index, camera in enumerate(cameras):
            key = self._vm.camera_key(camera)
            preview = self._previews_by_camera[key]
            row, col = divmod(index, self._grid_columns)
            self._grid.addWidget(preview, row, col)

    def _sync_empty_state_visibility(self) -> None:
        self._empty_state.setVisible(not self._vm.has_cameras())
