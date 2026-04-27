from typing import override

from PySide6 import QtCore, QtWidgets

from ppe_client.application.cameras import CameraSessionService
from ppe_client.application.cameras.ports import CameraEnumerator
from ppe_client.application.poses import PoseService
from ppe_client.domain import CameraDescriptor
from ppe_client.presentation.widgets.camera_capture import (
    CameraCaptureViewModel,
    CameraCaptureWidget,
)

from ...dialogs.select_camera import SelectCameraDialog, SelectCameraViewModel
from ...routing.core import Screen
from .training_view_model import TrainingViewModel


class TrainingScreen(Screen[TrainingViewModel]):
    _capture_widgets: list[CameraCaptureWidget]

    @override
    def on_create(self) -> None:
        self._view_model.open_camera_selection_dialog.connect(
            self._on_open_camera_selection_dialog
        )
        self._view_model.new_camera_added.connect(self._on_new_camera_added)
        self._view_model.camera_not_added.connect(self._on_camera_not_added)
        self._view_model.clear_cameras.connect(self._on_clear_cameras)
        self._capture_widgets = []

        self._empty_state = QtWidgets.QLabel("No cameras selected")
        self._empty_state.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._grid = QtWidgets.QGridLayout()
        self._grid.setSpacing(8)

        previews_container = QtWidgets.QWidget(self)
        previews_container.setLayout(self._grid)

        self._scroll = QtWidgets.QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(previews_container)

        self._add_camera_button = QtWidgets.QPushButton("Add Camera")
        self._add_camera_button.clicked.connect(
            self._view_model.on_add_camera_button_clicked
        )

        self._clear_button = QtWidgets.QPushButton("Clear")
        self._clear_button.clicked.connect(self._view_model.on_clear_button_clicked)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self._add_camera_button)
        controls.addWidget(self._clear_button)
        controls.addStretch(1)

        root = QtWidgets.QVBoxLayout(self)

        root.addWidget(self._scroll)
        root.addWidget(self._empty_state)
        root.addLayout(controls)
        self.setLayout(root)

    @override
    def on_enter(self) -> None:
        for capture_widget in self._capture_widgets:
            capture_widget.start_capture()

    @override
    def on_leave(self) -> None:
        for capture_widget in self._capture_widgets:
            capture_widget.stop_capture()

    @override
    def on_destroy(self) -> None:
        self._view_model.open_camera_selection_dialog.disconnect(
            self._on_open_camera_selection_dialog
        )
        self._clear_button.clicked.disconnect(self._view_model.on_clear_button_clicked)
        self._add_camera_button.clicked.disconnect(
            self._view_model.on_add_camera_button_clicked
        )

        self._view_model.new_camera_added.disconnect(self._on_new_camera_added)
        self._view_model.camera_not_added.disconnect(self._on_camera_not_added)
        self._view_model.clear_cameras.disconnect(self._on_clear_cameras)
        super().on_destroy()

    @QtCore.Slot(object)
    def _on_open_camera_selection_dialog(
        self, camera_enumerator: CameraEnumerator
    ) -> None:
        dialog_view_model = SelectCameraViewModel(camera_enumerator)
        dialog = SelectCameraDialog(dialog_view_model, self)

        match dialog.exec():
            case QtWidgets.QDialog.DialogCode.Accepted:
                selected_camera = dialog.get_selected_camera_info()
                self._view_model.open_camera(selected_camera)
            case QtWidgets.QDialog.DialogCode.Rejected:
                print("Rejected")

    @QtCore.Slot(str)
    def _on_camera_not_added(self, message: str) -> None:
        QtWidgets.QMessageBox.information(self, "Camera Not Added", message)

    @QtCore.Slot(object)
    def _on_new_camera_added(
        self,
        session_service: CameraSessionService,
        pose_service: PoseService,
        camera: CameraDescriptor,
    ) -> None:
        capture_widget = self._create_capture_widget(
            session_service, pose_service, camera
        )

        row, col = divmod(len(self._capture_widgets), 2)
        self._grid.addWidget(capture_widget, row, col)
        self._empty_state.hide()
        self._scroll.show()
        self._capture_widgets.append(capture_widget)

    def _create_capture_widget(
        self,
        session_service: CameraSessionService,
        pose_service: PoseService,
        camera: CameraDescriptor,
    ) -> CameraCaptureWidget:
        capture_view_model = CameraCaptureViewModel(
            session_service, pose_service, camera
        )
        capture_widget = CameraCaptureWidget(capture_view_model, self)

        capture_widget.setMinimumHeight(240)
        capture_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        return capture_widget

    @QtCore.Slot()
    def _on_clear_cameras(self) -> None:
        for capture_widget in self._capture_widgets:
            self._grid.removeWidget(capture_widget)
            capture_widget.close()
            capture_widget.deleteLater()
        self._capture_widgets.clear()
        self._empty_state.show()
        self._scroll.hide()
