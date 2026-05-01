from wireup import SyncContainer, create_sync_container, injectable

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.sensors import (
    BleakSensorRegistry,
)
from ppe_client.application.sensors.calibration import (
    MeanSensorCalibrator,
    SensorCalibrator,
)
from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.presentation.screens.choose_exercise import (
    ChooseExerciseViewModel,
)
from ppe_client.presentation.screens.sensor_calibration import (
    SensorCalibrationViewModel,
)
from ppe_client.presentation.screens.sensor_connection import (
    SensorConnectionViewModel,
)
from ppe_client.presentation.screens.sensor_discovery import (
    SensorDiscoveryViewModel,
)


@injectable
def make_exercise_session() -> ExerciseSession:
    return ExerciseSession()


def create_container() -> SyncContainer:
    """
    Create a new DI container.
    """
    return create_sync_container(
        injectables=[
            make_exercise_session,
            injectable(MeanSensorCalibrator, as_type=SensorCalibrator),
            BleakSensorRegistry,
            injectable(SensorService),
            ChooseExerciseViewModel,
            SensorDiscoveryViewModel,
            SensorConnectionViewModel,
            SensorCalibrationViewModel,
        ]
    )
