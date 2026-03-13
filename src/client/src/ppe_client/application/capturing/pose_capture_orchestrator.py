from PySide6 import QtCore

from ppe_client.application.ports import CameraGateway, PoseLandmarkerFactory
from ppe_client.domain import CameraDescriptor, CameraIdentity

from .pose_capture_session import PoseCaptureSession

type CameraSessionKey = CameraIdentity


class PoseCaptureOrchestrator(QtCore.QObject):
    """Coordinate shared lifecycle of pose capture sessions per camera."""

    _sessions: dict[CameraSessionKey, tuple[PoseCaptureSession, int]]
    _stop_retry_attempts: dict[CameraSessionKey, int]
    _camera_service: CameraGateway
    _pose_landmarker_factory: PoseLandmarkerFactory
    _max_stop_retry_attempts: int
    _is_shutting_down: bool

    _STOP_RETRY_DELAY_MS = 300

    def __init__(
        self,
        /,
        camera_service: CameraGateway,
        pose_landmarker_factory: PoseLandmarkerFactory,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._camera_service = camera_service
        self._pose_landmarker_factory = pose_landmarker_factory
        self._sessions = {}
        self._stop_retry_attempts = {}
        self._max_stop_retry_attempts = 3
        self._is_shutting_down = False

    def connect_session(self, camera_info: CameraDescriptor) -> PoseCaptureSession:
        if self._is_shutting_down:
            raise RuntimeError("Cannot connect capture session during shutdown")

        self._collect_sessions()

        key = camera_info.identity
        current = self._sessions.get(key)
        if current is not None:
            session, refs = current
            self._sessions[key] = (session, refs + 1)
            if not session.is_running and not session.is_stopping_failed:
                session.start()
            return session

        session = PoseCaptureSession(
            camera_info=camera_info,
            camera_service=self._camera_service,
            pose_landmarker_factory=self._pose_landmarker_factory,
            parent=self,
        )
        session.finished.connect(self._collect_sessions)
        session.failed_stopping.connect(self._collect_sessions)
        self._sessions[key] = (session, 1)
        session.start()
        return session

    def disconnect_session(self, camera_info: CameraDescriptor) -> None:
        key = camera_info.identity
        current = self._sessions.get(key)
        if current is None:
            return

        session, refs = current
        if refs > 1:
            self._sessions[key] = (session, refs - 1)
            return

        self._sessions[key] = (session, 0)
        self._collect_sessions()

    @QtCore.Slot()
    def _collect_sessions(self) -> None:
        removable: list[CameraSessionKey] = []
        should_schedule_retry = False

        for key, (session, refs) in self._sessions.items():
            if refs > 0:
                self._stop_retry_attempts.pop(key, None)
                continue

            if session.is_running:
                session.stop()

            if session.is_stopping_failed:
                attempt = self._stop_retry_attempts.get(key, 0) + 1
                self._stop_retry_attempts[key] = attempt
                if attempt < self._max_stop_retry_attempts:
                    should_schedule_retry = True
                    continue

            if session.is_running:
                continue

            removable.append(key)

        for key in removable:
            session, _ = self._sessions.pop(key)
            self._stop_retry_attempts.pop(key, None)
            session.deleteLater()

        if should_schedule_retry and not self._is_shutting_down:
            QtCore.QTimer.singleShot(self._STOP_RETRY_DELAY_MS, self._collect_sessions)

    @QtCore.Slot()
    def shutdown(self) -> None:
        self._is_shutting_down = True

        for key, (session, _) in list(self._sessions.items()):
            self._sessions[key] = (session, 0)

        for _ in range(self._max_stop_retry_attempts):
            has_running_sessions = False
            for session, _ in self._sessions.values():
                if not session.is_running:
                    continue

                session.stop()
                if session.is_running:
                    has_running_sessions = True

            if not has_running_sessions:
                break

        for key, (session, _) in list(self._sessions.items()):
            if session.is_running:
                continue

            self._sessions.pop(key)
            self._stop_retry_attempts.pop(key, None)
            session.deleteLater()
