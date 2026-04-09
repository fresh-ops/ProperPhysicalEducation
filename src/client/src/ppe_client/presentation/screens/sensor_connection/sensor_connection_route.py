from ...routing.core import RouteDescriptor
from .sensor_connection_payload import SensorConnectionPayload
from .sensor_connection_screen import SensorConnectionScreen
from .sensor_connection_view_model import SensorConnectionViewModel

sensor_connection_route_descriptor = RouteDescriptor(
    SensorConnectionPayload, SensorConnectionViewModel, SensorConnectionScreen
)
