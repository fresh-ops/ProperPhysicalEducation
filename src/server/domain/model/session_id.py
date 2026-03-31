from dataclasses import dataclass


@dataclass(frozen=True)
class SessionId:
    id: str
