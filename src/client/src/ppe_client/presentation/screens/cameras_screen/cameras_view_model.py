import asyncio

from PySide6 import QtCore

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.network.schemas import FeedbackResponse
from ppe_client.domain import CameraDescriptor, CameraIdentity

from .cameras_payload import CamerasPayload


class CamerasViewModel(QtCore.QObject):
    cameras_changed = QtCore.Signal(list)

    _cameras_by_key: dict[CameraIdentity, CameraDescriptor]
    _exercise_session: ExerciseSession

    def __init__(
        self, exercise_session: ExerciseSession, parent: QtCore.QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._cameras_by_key = {}
        self._exercise_session = exercise_session

    def bind_model(self, payload: CamerasPayload | None = None) -> None:
        if payload is None:
            return
        loop = asyncio.get_running_loop()
        loop.create_task(  # noqa: RUF006
            self._exercise_session.start(payload.exercise_id, self._show_feedback)
        )

    def stop(self) -> None:
        loop = asyncio.get_running_loop()
        loop.create_task(self._exercise_session.close())  # noqa: RUF006

    def add_camera(self, camera_info: CameraDescriptor) -> bool:
        key = camera_info.identity
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

    def _show_feedback(self, feedback: FeedbackResponse) -> None:
        for message in feedback.feedbacks:
            print(message)
