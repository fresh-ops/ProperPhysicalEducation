from wireup import AsyncContainer, create_async_container, injectable

from application.usecase.evaluate_exercise_use_case import EvaluateExerciseUseCase
from application.usecase.get_exercises_use_case import GetExercisesUseCase
from application.usecase.start_session_use_case import StartSessionUseCase
from config import settings
from composition.di import (
    application_di,
    infrastructure_di,
)


injectables = [
    injectable(GetExercisesUseCase),
    injectable(StartSessionUseCase),
    injectable(EvaluateExerciseUseCase),
    application_di,
    infrastructure_di,
]


def create_container() -> AsyncContainer:
    """
    Create a new DI container.
    """
    return create_async_container(
        config=settings.model_dump(),
        injectables=injectables,
    )
