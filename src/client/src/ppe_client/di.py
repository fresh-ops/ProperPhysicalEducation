from wireup import SyncContainer, create_sync_container, injectable

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.sensors.bleak_sensor_connector import BleakSensorConnector
from ppe_client.adapters.sensors.bleak_sensor_enumerator import BleakSensorEnumerator
from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.presentation.screens.choose_exercise.choose_exercise_view_model import (
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
            BleakSensorEnumerator,
            BleakSensorConnector,
            SensorService,
            ChooseExerciseViewModel,
            SensorDiscoveryViewModel,
            SensorConnectionViewModel,
            SensorCalibrationViewModel,
        ]
    )
