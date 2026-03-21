from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Landmark:
    x: float | None = None
    y: float | None = None
    z: float | None = None
    visibility: float | None = None
    presence: float | None = None

    @property
    def weight(self) -> float:
        if self.visibility is not None and self.presence is not None:
            return self.visibility * self.presence
        elif self.visibility is not None:
            return self.visibility
        elif self.presence is not None:
            return self.presence
        return 0


@dataclass(frozen=True, slots=True)
class Pose:
    landmarks: list[Landmark]
    timestamp_ms: int
