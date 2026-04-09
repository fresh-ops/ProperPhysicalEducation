from wireup import SyncContainer, create_sync_container, injectable

from ppe_client.adapters.network import ExerciseSession
from ppe_client.presentation.screens.choose_exercise.choose_exercise_view_model import (
    ChooseExerciseViewModel,
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
            # Services
            make_exercise_session,
            # ViewModels
            ChooseExerciseViewModel,
        ]
    )
