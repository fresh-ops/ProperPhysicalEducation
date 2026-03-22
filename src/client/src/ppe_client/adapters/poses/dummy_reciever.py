from ppe_client.application.poses import Pose
from ppe_client.domain import CameraDescriptor


class DummyReciever:
    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None:
        pass
