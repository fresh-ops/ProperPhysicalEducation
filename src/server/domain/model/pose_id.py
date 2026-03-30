from dataclasses import dataclass


@dataclass(frozen=True)
class PoseId:
    id: str
