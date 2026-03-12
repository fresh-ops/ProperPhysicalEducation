from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore

from src.poses.cameras import CameraService

from .pose_capture_session import PoseCaptureSession

type CameraSessionKey = tuple[int, int]


class PoseCaptureOrchestrator(QtCore.QObject):
    """Coordinate shared lifecycle of pose capture sessions per camera.

    The orchestrator keeps one ``PoseCaptureSession`` per camera and tracks
    reference counts for consumers interested in that camera stream.

    Sessions are started on first consumer connect and stopped when last
    consumer disconnects.
    """

    _sessions: dict[CameraSessionKey, tuple[PoseCaptureSession, int]]
    _stop_retry_attempts: dict[CameraSessionKey, int]
    _camera_service: CameraService
    _max_stop_retry_attempts: int
    _is_shutting_down: bool

    _STOP_RETRY_DELAY_MS = 300

    def __init__(
        self, /, camera_service: CameraService, parent: QtCore.QObject | None = None
    ) -> None:
        """Initialize orchestrator state and capture dependencies.

        Args:
            camera_service (CameraService): Camera provider used by sessions.
            parent (QtCore.QObject | None): Optional parent for Qt ownership.
        """
        super().__init__(parent)
        self._camera_service = camera_service
        self._sessions = {}
        self._stop_retry_attempts = {}
        self._max_stop_retry_attempts = 3
        self._is_shutting_down = False

    def connect_session(self, camera_info: CameraInfo) -> PoseCaptureSession:
        """Acquire session for camera and increment its consumer counter.

        Args:
            camera_info (CameraInfo): Camera descriptor to connect.

        Returns:
            PoseCaptureSession: Shared session for the selected camera.

        Raises:
            RuntimeError: If orchestrator is shutting down.
        """
        if self._is_shutting_down:
            raise RuntimeError("Cannot connect capture session during shutdown")

        self._collect_sessions()

        key = self._camera_key(camera_info)
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
            parent=self,
        )
        session.finished.connect(self._collect_sessions)
        session.failed_stopping.connect(self._collect_sessions)
        self._sessions[key] = (session, 1)
        session.start()
        return session

    def disconnect_session(self, camera_info: CameraInfo) -> None:
        """Release one consumer reference from camera session.

        Args:
            camera_info (CameraInfo): Camera descriptor to disconnect.
        """
        key = self._camera_key(camera_info)
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
        """Stop and remove sessions that no longer have consumers.

        For sessions that fail cooperative stop, retry collection up to a
        limited number of attempts with a short delay.
        """
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
        """Stop all sessions before application teardown.

        This method performs bounded, synchronous stop attempts to reduce
        the chance of worker activity during interpreter shutdown.
        """
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

    def _camera_key(self, camera_info: CameraInfo) -> CameraSessionKey:
        """Build a stable dictionary key for camera descriptor.

        Args:
            camera_info (CameraInfo): Camera descriptor from camera service.

        Returns:
            CameraSessionKey: Tuple of backend and index.
        """
        return (camera_info.backend, camera_info.index)
