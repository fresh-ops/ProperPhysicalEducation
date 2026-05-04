from dataclasses import dataclass

from ppe_client.domain import SensorDescriptor

from ...routing.core import Payload


@dataclass(frozen=True, slots=True)
class SensorConnectionPayload(Payload):
    descriptor: SensorDescriptor
