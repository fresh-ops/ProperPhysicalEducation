from ...routing.core import RouteDescriptor
from .training_payload import TrainingPayload
from .training_screen import TrainingScreen
from .training_view_model import TrainingViewModel

training_route_descriptor = RouteDescriptor(
    TrainingPayload, TrainingViewModel, TrainingScreen
)
