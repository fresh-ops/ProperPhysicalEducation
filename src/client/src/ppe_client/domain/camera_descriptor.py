from dataclasses import dataclass

type CameraIdentity = tuple[int, int]


@dataclass(frozen=True, slots=True)
class CameraDescriptor:
    """Domain-level camera metadata used across application and presentation."""

    name: str
    index: int
    backend: int

    @property
    def identity(self) -> CameraIdentity:
        """Return a stable identity key for this camera descriptor."""
        return (self.backend, self.index)
