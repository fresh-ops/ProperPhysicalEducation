from dataclasses import dataclass

from domain.model.emg import EmgReading
from domain.model.pose import Pose


@dataclass(frozen=True)
class ProcessContext:
    pose: Pose
    emgs: list[EmgReading]
