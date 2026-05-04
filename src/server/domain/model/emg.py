from dataclasses import dataclass

from domain.model.zone import Zone


@dataclass(frozen=True)
class EmgReading:
    sensor_id: str
    zone: Zone
