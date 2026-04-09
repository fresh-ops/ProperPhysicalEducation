from ...routing.core import RouteDescriptor
from .choose_exercise_payload import ChooseExercisePayload
from .choose_exercise_screen import ChooseExerciseScreen
from .choose_exercise_view_model import ChooseExerciseViewModel

choose_exercise_route_descriptor = RouteDescriptor(
    ChooseExercisePayload, ChooseExerciseViewModel, ChooseExerciseScreen
)
