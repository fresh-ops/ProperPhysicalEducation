from dataclasses import dataclass


@dataclass(frozen=True)
class PoseId:
    id: str

    def __str__(self) -> str:
        return self.id
