from wireup import SyncContainer, create_sync_container, injectable

from ppe_client import presentation
from ppe_client.adapters.cameras import (
    RefCountedCameraSessionStorage,
    SessionTerminator,
)
from ppe_client.adapters.cameras.open_cv import (
    OpenCVCameraEnumerator,
    OpenCVCameraSessionFactory,
)
from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.poses import MediaPipePoseDetectorFactory
from ppe_client.adapters.poses.restoration import PoseRestorer
from ppe_client.adapters.sensors import (
    BleakSensorRegistry,
)
from ppe_client.application.cameras import CameraSessionService
from ppe_client.application.cameras.ports import (
    CameraEnumerator,
    CameraSessionFactory,
    CameraSessionStorage,
)
from ppe_client.application.poses import PoseService
from ppe_client.application.poses.ports import PoseDetectorFactory, PoseReciever
from ppe_client.application.sensors.calibration import (
    MeanSensorCalibrator,
    SensorCalibrator,
)
from ppe_client.application.sensors.sensor_service import SensorService


@injectable
def make_pose_service(
    detector_factory: PoseDetectorFactory, restorer: PoseRestorer
) -> PoseService:
    return PoseService(detector_factory, restorer)


@injectable
def make_exercise_session() -> ExerciseSession:
    return ExerciseSession()


injectables = [
    make_exercise_session,
    injectable(ExerciseSession, as_type=PoseReciever),
    injectable(OpenCVCameraEnumerator, as_type=CameraEnumerator),
    injectable(SessionTerminator),
    injectable(RefCountedCameraSessionStorage, as_type=CameraSessionStorage),
    injectable(OpenCVCameraSessionFactory, as_type=CameraSessionFactory),
    injectable(CameraSessionService),
    injectable(MediaPipePoseDetectorFactory, as_type=PoseDetectorFactory),
    injectable(PoseRestorer),
    make_pose_service,
    injectable(MeanSensorCalibrator, as_type=SensorCalibrator),
    BleakSensorRegistry,
    injectable(SensorService),
    # ViewModels
    presentation,
]


def create_container() -> SyncContainer:
    """
    Create a new DI container.
    """
    return create_sync_container(injectables=injectables)
