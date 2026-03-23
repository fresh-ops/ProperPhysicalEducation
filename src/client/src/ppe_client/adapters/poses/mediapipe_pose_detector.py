from collections.abc import Callable

import mediapipe as mp
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
)
from PySide6 import QtCore

from ppe_client.application.cameras import Frame
from ppe_client.application.poses import Landmark, Pose

from ..cameras.frame_converter import FrameConverter


class MediaPipePoseDetector(QtCore.QObject):
    _callbacks: list[Callable[[Pose | None, Frame], None]]
    _lock: QtCore.QMutex
    _worker: "_DetectorWorker"

    def __init__(self, pose_landmarker: PoseLandmarker) -> None:
        super().__init__()
        self._callbacks = []
        self._lock = QtCore.QMutex()
        self._worker = _DetectorWorker(pose_landmarker, self)
        self._worker.pose_ready.connect(self._on_pose_ready)
        self._worker.start()

    def detect(
        self, frame: Frame, callback: Callable[[Pose | None, Frame], None]
    ) -> None:
        self._lock.lock()
        try:
            self._callbacks.append(callback)
            self._worker.add_frame(frame)
        finally:
            self._lock.unlock()

    def close(self) -> None:
        self._worker.stop()

    @QtCore.Slot(object)
    def _on_pose_ready(self, pose: Pose | None, frame: Frame) -> None:
        self._lock.lock()
        try:
            self._callbacks.pop(0)(pose, frame)
        finally:
            self._lock.unlock()


class _DetectorWorker(QtCore.QThread):
    pose_ready = QtCore.Signal(object, object)

    _pose_landmarker: PoseLandmarker
    _lock: QtCore.QMutex
    _running: bool
    _frames: list[Frame]

    def __init__(
        self, pose_landmarker: PoseLandmarker, parent: QtCore.QObject | None = None
    ):
        super().__init__(parent=parent)
        self._pose_landmarker = pose_landmarker
        self._lock = QtCore.QMutex()
        self._running = True
        self._frames = []

    def add_frame(self, frame: Frame) -> None:
        self._lock.lock()
        self._frames.append(frame)
        self._lock.unlock()

    @QtCore.Slot()
    def run(self) -> None:
        while self._running:
            self._lock.lock()
            if self._frames:
                frame = self._frames.pop(0)
                self._lock.unlock()

                result = self._detect(frame)
                self.pose_ready.emit(result, frame)
            else:
                self._lock.unlock()
                self.msleep(10)

        self._pose_landmarker.close()

    def stop(self) -> None:
        self._running = False

    def _detect(self, frame: Frame) -> Pose | None:
        image = FrameConverter.to_ndarray(frame)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        result = self._pose_landmarker.detect_for_video(
            mp_image, timestamp_ms=frame.timestamp_ms
        )
        if len(result.pose_landmarks) == 0:
            return None
        landmarks = [
            Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                presence=landmark.presence,
            )
            for landmark in result.pose_landmarks[0]
        ]

        return Pose(landmarks, frame.timestamp_ms)
