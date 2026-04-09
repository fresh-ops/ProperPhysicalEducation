from dataclasses import dataclass

SensorIdentity = str


@dataclass(frozen=True, slots=True)
class SensorDescriptor:
    name: str
    address: str

    @property
    def identity(self) -> SensorIdentity:
        return self.address
