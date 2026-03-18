from PySide6 import QtCore

from ppe_client.application.ports import CameraSession


class SessionTerminator(QtCore.QObject):
    _sessions_to_terminate: list[CameraSession]
    _lock: QtCore.QMutex
    _timer: QtCore.QTimer

    def __init__(self, interval_ms: int = 1000) -> None:
        super().__init__()
        self._sessions_to_terminate: list[CameraSession] = []
        self._lock = QtCore.QMutex()

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._terminate)
        self._timer.start()

    def claim(self, session: CameraSession) -> None:
        self._lock.lock()
        try:
            self._sessions_to_terminate.append(session)
        finally:
            self._lock.unlock()

    @QtCore.Slot()
    def _terminate(self) -> None:
        sessions: list[CameraSession] = []
        self._lock.lock()
        try:
            sessions = list(self._sessions_to_terminate)
        finally:
            self._lock.unlock()

        terminated: list[CameraSession] = []

        for session in sessions:
            success = session.terminate()
            if success:
                terminated.append(session)

        self._lock.lock()
        try:
            self._sessions_to_terminate = [
                s for s in self._sessions_to_terminate if s not in terminated
            ]
        finally:
            self._lock.unlock()
