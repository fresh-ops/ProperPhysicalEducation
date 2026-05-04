from ...routing.core import RouteDescriptor
from .sensor_calibration_payload import SensorCalibrationPayload
from .sensor_calibration_screen import SensorCalibrationScreen
from .sensor_calibration_view_model import SensorCalibrationViewModel

sensor_calibration_route_descriptor = RouteDescriptor(
    SensorCalibrationPayload, SensorCalibrationViewModel, SensorCalibrationScreen
)
