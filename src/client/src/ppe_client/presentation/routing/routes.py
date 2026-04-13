from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Routes:
    CHOOSE_EXERCISE = "choose_exercise"
    TRAINING = "training"
