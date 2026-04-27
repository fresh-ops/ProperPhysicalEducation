from collections.abc import Callable

from ppe_client.domain import CameraDescriptor, CameraIdentity

from ..cameras.frame import Frame
from ..poses.pose import Pose
from .ports.pose_detector import PoseDetector
from .ports.pose_detector_factory import PoseDetectorFactory
from .ports.pose_reciever import PoseReciever


class PoseService:
    _detector_factory: PoseDetectorFactory
    _detectors: dict[CameraIdentity, PoseDetector]
    _reciever: PoseReciever

    def __init__(
        self, detector_factory: PoseDetectorFactory, reciever: PoseReciever
    ) -> None:
        self._detector_factory = detector_factory
        self._detectors = {}
        self._reciever = reciever

    def detect(
        self,
        camera: CameraDescriptor,
        frame: Frame,
        callback: Callable[[Pose | None, Frame], None],
    ) -> None:
        detector = self._get_detector_for(camera)
        detector.detect(
            frame, lambda p, f: self._on_pose_detected(camera, p, f, callback)
        )

    def _get_detector_for(self, camera: CameraDescriptor) -> PoseDetector:
        if camera.identity not in self._detectors:
            self._detectors[camera.identity] = self._detector_factory.create()
        return self._detectors[camera.identity]

    def _on_pose_detected(
        self,
        camera: CameraDescriptor,
        pose: Pose | None,
        frame: Frame,
        callback: Callable[[Pose | None, Frame], None],
    ) -> None:
        if pose:
            self._reciever.recieve(pose, camera)
        callback(pose, frame)
