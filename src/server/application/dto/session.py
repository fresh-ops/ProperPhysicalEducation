from dataclasses import dataclass


@dataclass
class StartSessionRequestDto:
    exercise_id: str


@dataclass
class StartSessionResponseDto:
    session_id: str
