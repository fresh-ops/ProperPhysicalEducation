from dataclasses import dataclass

from ...routing import Payload


@dataclass
class CamerasPayload(Payload):
    exercise_id: int
