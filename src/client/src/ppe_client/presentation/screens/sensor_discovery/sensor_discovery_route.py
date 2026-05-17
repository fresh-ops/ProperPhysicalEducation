from ...routing.core import RouteDescriptor
from .sensor_discovery_payload import SensorDiscoveryPayload
from .sensor_discovery_screen import SensorDiscoveryScreen
from .sensor_discovery_view_model import SensorDiscoveryViewModel

sensor_discovery_route_descriptor = RouteDescriptor(
    SensorDiscoveryPayload, SensorDiscoveryViewModel, SensorDiscoveryScreen
)
