from dataclasses import dataclass

from ...routing.core import Payload


@dataclass(frozen=True, slots=True)
class SensorDiscoveryPayload(Payload):
    pass
