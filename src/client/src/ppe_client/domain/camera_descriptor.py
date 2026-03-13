from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CameraDescriptor:
    """Domain-level camera metadata used across application and presentation."""

    name: str
    index: int
    backend: int
