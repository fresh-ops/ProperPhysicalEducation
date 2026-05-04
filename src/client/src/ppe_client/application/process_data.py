from dataclasses import dataclass

from ppe_client.application.poses.pose import Pose
from ppe_client.application.sensors.calibration.calibration_data import ValueZone


@dataclass(frozen=True, slots=True)
class EmgReading:
    sensor_name: str
    zone: ValueZone


@dataclass(frozen=True, slots=True)
class ProcessData:
    pose: Pose
    emgs: list[EmgReading]
