from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.application.cameras import CameraSessionService
from ppe_client.application.cameras.ports import CameraEnumerator
from ppe_client.application.poses import PoseService
from ppe_client.domain import CameraDescriptor, CameraIdentity

from ...routing.core import ViewModel
from .training_payload import TrainingPayload


@injectable(lifetime="transient")
class TrainingViewModel(ViewModel[TrainingPayload]):
    open_camera_selection_dialog = QtCore.Signal(object)
    new_camera_added = QtCore.Signal(object, object, object)
    camera_not_added = QtCore.Signal(str)
    clear_cameras = QtCore.Signal()

    _camera_enumerator: CameraEnumerator
    _camera_session_service: CameraSessionService
    _pose_service: PoseService
    _cameras: dict[CameraIdentity, CameraDescriptor]

    def __init__(
        self,
        camera_enumerator: CameraEnumerator,
        camera_session_service: CameraSessionService,
        pose_service: PoseService,
    ) -> None:
        super().__init__()
        self._camera_enumerator = camera_enumerator
        self._camera_session_service = camera_session_service
        self._pose_service = pose_service
        self._cameras = {}

    @override
    async def on_enter(self, payload: TrainingPayload | None = None) -> None:
        if not payload:
            return

    @QtCore.Slot()
    def on_add_camera_button_clicked(self) -> None:
        self.open_camera_selection_dialog.emit(self._camera_enumerator)

    def open_camera(self, camera: CameraDescriptor) -> None:
        key = camera.identity
        if key in self._cameras:
            self.camera_not_added.emit("Selected camera is already displayed")
        else:
            self._cameras[key] = camera
            self.new_camera_added.emit(
                self._camera_session_service, self._pose_service, camera
            )

    @QtCore.Slot()
    def on_clear_button_clicked(self) -> None:
        self._cameras.clear()
        self.clear_cameras.emit()
