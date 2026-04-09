from wireup import SyncContainer, create_sync_container, injectable

from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.sensors.bleak_sensor_connector import BleakSensorConnector
from ppe_client.adapters.sensors.bleak_sensor_enumerator import BleakSensorEnumerator
from ppe_client.application.sensors.sensor_service import SensorService
from ppe_client.presentation.screens.choose_exercise.choose_exercise_view_model import (
    ChooseExerciseViewModel,
)
from ppe_client.presentation.screens.sensor_discovery import (
    SensorDiscoveryViewModel,
)


@injectable
def make_exercise_session() -> ExerciseSession:
    return ExerciseSession()


@injectable
def make_sensor_enumerator() -> BleakSensorEnumerator:
    return BleakSensorEnumerator()


@injectable
def make_sensor_connector() -> BleakSensorConnector:
    return BleakSensorConnector()


def create_container() -> SyncContainer:
    """
    Create a new DI container.
    """
    return create_sync_container(
        injectables=[
            make_exercise_session,
            make_sensor_enumerator,
            make_sensor_connector,
            SensorService,
            ChooseExerciseViewModel,
            SensorDiscoveryViewModel,
        ]
    )