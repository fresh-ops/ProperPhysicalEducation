from collections.abc import Callable

from cv2 import CAP_PROP_POS_MSEC, VideoCapture
from cv2.typing import MatLike
from PySide6 import QtCore

from ppe_client.application.cameras import Frame, FrameOrigin


class OpenCVCameraSession(QtCore.QObject):
    _worker: "_CaptureWorker | None"
    _thread: QtCore.QThread | None
    _callbacks: list[Callable[[Frame], None]]

    def __init__(self, camera: VideoCapture) -> None:
        super().__init__()
        self._callbacks = []
        self._worker = None
        self._thread = None

        if not camera.isOpened():
            raise RuntimeError("Failed to open camera source.")

        self._start(camera)

    def attach(self, callback: Callable[[Frame], None]) -> None:
        print("Attach")
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def detach(self, callback: Callable[[Frame], None]) -> None:
        print("Detach")
        try:
            self._callbacks.remove(callback)
        except ValueError:
            print("No such callback attached.")

    def terminate(self) -> bool:
        if self._worker:
            self._worker.stop()
        if self._thread:
            self._thread.quit()
            return self._thread.wait(1_500)
        return True

    def _start(self, camera: VideoCapture) -> None:
        if self._worker is not None or self._thread is not None:
            return

        self._worker = _CaptureWorker(camera)
        self._thread = QtCore.QThread()
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.frame_ready.connect(self._on_frame_ready)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.destroyed.connect(self._clear_refs)

        self._thread.start()

    def _clear_refs(self) -> None:
        self._worker = None
        self._thread = None

    def _on_frame_ready(self, cv_image: MatLike, timestamp_ms: float) -> None:
        callbacks_snapshor = list(self._callbacks)

        if not callbacks_snapshor:
            return

        frame = Frame(
            cv_image.tobytes(), cv_image.shape, int(timestamp_ms), FrameOrigin.CV2
        )

        for callback in self._callbacks:
            try:
                callback(frame)
            except Exception as e:
                print(f"Error in callback: {e}.")


class _CaptureWorker(QtCore.QObject):
    frame_ready = QtCore.Signal(object, float)
    finished = QtCore.Signal()

    _capture: VideoCapture
    _is_running: bool

    def __init__(self, camera: VideoCapture) -> None:
        super().__init__()
        self._capture = camera
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @QtCore.Slot()
    def run(self) -> None:
        if not self._capture.isOpened():
            self._capture.release()
            self.finished.emit()
            return
        self._is_running = True

        try:
            while self._is_running:
                success, cv_image = self._capture.read()
                if not success:
                    continue

                timestamp_ms = self._capture.get(CAP_PROP_POS_MSEC)
                self.frame_ready.emit(cv_image, timestamp_ms)
        finally:
            self._capture.release()
            self._is_running = False
            self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        self._is_running = False
