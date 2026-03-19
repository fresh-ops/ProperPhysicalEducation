from dataclasses import dataclass

from PySide6 import QtCore

from ppe_client.application.ports import CameraSession, CameraSessionFactory
from ppe_client.domain import CameraDescriptor, CameraIdentity

from .session_terminator import SessionTerminator


@dataclass(slots=True)
class _SessionConnectionCounter:
    session: CameraSession
    connections: int


class RefCountedCameraSessionStorage:
    _sessions: dict[CameraIdentity, _SessionConnectionCounter]
    _lock: QtCore.QMutex
    _terminator: SessionTerminator

    def __init__(self, terminator: SessionTerminator) -> None:
        self._sessions = {}
        self._lock = QtCore.QMutex()
        self._terminator = terminator

    def acquire(
        self, camera: CameraDescriptor, session_factory: CameraSessionFactory
    ) -> CameraSession:
        key = camera.identity

        self._lock.lock()
        try:
            entry = self._sessions.get(key)

            if entry is None:
                session = session_factory.create_for(camera)
                entry = _SessionConnectionCounter(session, 0)
                self._sessions[key] = entry

            entry.connections += 1
            return entry.session
        finally:
            self._lock.unlock()

    def release(self, camera: CameraDescriptor) -> None:
        """Release the session associated with the camera."""
        key = camera.identity
        session_to_stop: CameraSession | None = None

        self._lock.lock()
        try:
            entry = self._sessions.get(key)
            if entry is None:
                return

            entry.connections -= 1
            if entry.connections <= 0:
                del self._sessions[key]
                session_to_stop = entry.session
        finally:
            self._lock.unlock()

        if session_to_stop is not None:
            self._terminator.claim(session_to_stop)
