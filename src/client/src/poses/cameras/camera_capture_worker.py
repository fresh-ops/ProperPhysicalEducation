import cv2
from cv2_enumerate_cameras.camera_info import CameraInfo
from PySide6 import QtCore, QtGui


class CameraCaptureWorker(QtCore.QObject):
    """Background worker that reads frames from OpenCV camera capture.

    Signals:
        frame_ready: Emitted with a ``QImage`` for each successfully read frame.
        finished: Emitted when capture loop exits or camera cannot be opened.
    """

    frame_ready = QtCore.Signal(QtGui.QImage)
    finished = QtCore.Signal()

    def __init__(
        self, camera_info: CameraInfo, parent: QtCore.QObject | None = None
    ) -> None:
        """Initialize worker state for a specific camera.

        Args:
            camera_info (CameraInfo): Camera metadata containing index and backend
                used to open the capture device.
            parent (QtCore.QObject | None): Optional parent QObject for Qt
                ownership.
        """
        super().__init__(parent)
        self._camera_info = camera_info
        self._running = True

    @QtCore.Slot()
    def run(self) -> None:
        """Run continuous capture loop and emit converted Qt frames."""
        capture = cv2.VideoCapture(self._camera_info.index, self._camera_info.backend)
        if not capture.isOpened():
            self.finished.emit()
            return

        while self._running:
            success, cv_image = capture.read()
            if not success:
                continue

            h, w, ch = cv_image.shape
            qimg = QtGui.QImage(
                cv_image.data,
                w,
                h,
                ch * w,
                QtGui.QImage.Format.Format_BGR888,
            )
            self.frame_ready.emit(qimg.copy())

        capture.release()
        self.finished.emit()

    @QtCore.Slot()
    def stop(self) -> None:
        """Request capture loop termination on next iteration."""
        self._running = False
