from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Routes:
    CHOOSE_EXERCISE = "choose_exercise"
    SENSOR_DISCOVERY = "sensor_discovery"
    SENSOR_CONNECTION = "sensor_connection"
