from dataclasses import dataclass

from ...routing.core import Payload


@dataclass(frozen=True, slots=True)
class TrainingPayload(Payload):
    exercise_id: str
