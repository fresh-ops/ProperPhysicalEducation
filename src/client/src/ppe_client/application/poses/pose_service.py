from ppe_client.domain import CameraDescriptor

from ..cameras.frame import Frame
from ..poses.pose import Pose
from .ports.pose_detector import PoseDetector
from .ports.pose_detector_factory import PoseDetectorFactory
from .ports.pose_reciever import PoseReciever


class PoseService:
    _detector: PoseDetector
    _reciever: PoseReciever

    def __init__(
        self, detector_factory: PoseDetectorFactory, reciever: PoseReciever
    ) -> None:
        self._detector = detector_factory.create()
        self._reciever = reciever

    def detect(self, camera: CameraDescriptor, frame: Frame) -> Pose | None:
        pose = self._detector.detect(frame)
        if pose is None:
            return None

        self._reciever.recieve(camera, pose)
        return pose
