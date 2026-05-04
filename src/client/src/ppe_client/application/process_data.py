from dataclasses import dataclass
from enum import Enum

from ppe_client.application.poses.pose import Pose


class Zone(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass(frozen=True, slots=True)
class EmgReading:
    sensor_name: str
    zone: Zone


@dataclass(frozen=True, slots=True)
class ProcessData:
    pose: Pose
    emgs: list[EmgReading]
