import asyncio
import contextlib
from functools import partial
from typing import override

from PySide6 import QtCore
from wireup import injectable

from ppe_client.adapters.network.exersice_session import ExerciseSession
from ppe_client.adapters.poses.restoration.pose_restorer import PoseRestorer
from ppe_client.application.async_pose_reciever_wrapper import AsyncPoseReceiverWrapper
from ppe_client.application.cameras import CameraSessionService
from ppe_client.application.cameras.ports import CameraEnumerator
from ppe_client.application.feedback import Feedback
from ppe_client.application.poses import PoseService
from ppe_client.application.process_synchornizer import ProcessSynchronizer
from ppe_client.application.sensors.sensor_reader import SensorReader
from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.application.sensors.sensor_value import SensorValue
from ppe_client.domain import CameraDescriptor, CameraIdentity, SensorDescriptor

from ...routing.core import ViewModel
from ...stores import SensorStore
from .training_payload import TrainingPayload


@injectable(lifetime="transient")
class TrainingViewModel(ViewModel[TrainingPayload]):
    open_camera_selection_dialog = QtCore.Signal(object)
    new_camera_added = QtCore.Signal(object, object, object)
    camera_not_added = QtCore.Signal(str)
    clear_cameras = QtCore.Signal()

    _camera_enumerator: CameraEnumerator
    _camera_session_service: CameraSessionService
    _sensor_service: SensorService
    _sensor_store: SensorStore
    _pose_service: PoseService
    _pose_restorer: PoseRestorer
    _exercise_session: ExerciseSession
    _cameras: dict[CameraIdentity, CameraDescriptor]
    _sensors: list[SensorReader]
    _exercise_task: asyncio.Task[None] | None
    _synchronizer: ProcessSynchronizer | None

    def __init__(  # noqa: PLR0913
        self,
        camera_enumerator: CameraEnumerator,
        camera_session_service: CameraSessionService,
        sensor_service: SensorService,
        sensor_store: SensorStore,
        pose_service: PoseService,
        pose_restorer: PoseRestorer,
        exercise_session: ExerciseSession,
    ) -> None:
        super().__init__()
        self._camera_enumerator = camera_enumerator
        self._camera_session_service = camera_session_service
        self._sensor_service = sensor_service
        self._sensor_store = sensor_store
        self._pose_service = pose_service
        self._pose_restorer = pose_restorer
        self._exercise_session = exercise_session
        self._cameras = {}
        self._sensors = []
        self._exercise_task = None
        self._synchronizer = None

    @override
    async def on_enter(self, payload: TrainingPayload | None = None) -> None:
        if not payload:
            return
        await self._start_sensor_readers()
        await self._start_exercise(payload.exercise_id)

    @override
    async def on_destroy(self) -> None:
        self._cameras.clear()
        self.clear_cameras.emit()
        for sensor in self._sensors:
            await sensor.stop()
        if self._exercise_session is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._exercise_session.close()
        if self._exercise_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                self._exercise_task.cancel()
                await self._exercise_task

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

    async def _start_sensor_readers(self) -> None:
        for descriptor in await self._sensor_store.get_all():
            sensor = await self._sensor_service.get_sensor(descriptor)
            reader = SensorReader(
                sensor, partial(self._on_sensor_data, descriptor), self._on_sensor_error
            )
            await reader.start()
            self._sensors.append(reader)

    async def _start_exercise(self, exercise_id: str) -> None:
        await self._exercise_session.start(exercise_id, self._on_feedback)
        self._exercise_task = asyncio.create_task(self._feedback_loop())

    def _on_feedback(self, feedback: list[Feedback]) -> None:
        print(feedback)

    async def _feedback_loop(self) -> None:
        self._synchronizer = ProcessSynchronizer()
        synchronizer = self._synchronizer
        self._pose_restorer.set_reciever(
            AsyncPoseReceiverWrapper(lambda p, _: synchronizer.append_pose(p))
        )
        try:
            while True:
                feedback = await self._exercise_session.receive_feedbacks(
                    self._synchronizer.queue
                )
                self._on_feedback(feedback)
        finally:
            await self._synchronizer.stop()
            self._synchronizer = None
            self._pose_restorer.set_reciever(None)

    async def _on_sensor_data(
        self, descriptor: SensorDescriptor, value: SensorValue
    ) -> None:
        if self._synchronizer:
            await self._synchronizer.append_sensor(descriptor, value)
        print(value)

    def _on_sensor_error(self, e: Exception) -> None:
        print(e)
