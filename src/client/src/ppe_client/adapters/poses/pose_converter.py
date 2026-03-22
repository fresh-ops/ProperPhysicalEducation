import numpy as np
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from ppe_client.application.poses import Landmark, Pose


class PoseConverter:
    @classmethod
    def to_mediapipe(cls, pose: Pose) -> list[NormalizedLandmark]:
        result: list[NormalizedLandmark] = []

        for landmark in pose.landmarks:
            result.append(
                NormalizedLandmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    visibility=landmark.visibility,
                    presence=landmark.presence,
                    name=None,
                )
            )

        return result

    @classmethod
    def to_numpy(cls, pose: Pose) -> tuple[np.ndarray, np.ndarray]:
        coords: list[list[float]] = []
        weights: list[list[float]] = []

        for landmark in pose.landmarks:
            coords.append([landmark.x, landmark.y, landmark.z])
            weights.append([landmark.visibility or 1.0, landmark.presence or 1.0])

        return np.array(coords), np.array(weights)

    @classmethod
    def from_numpy(
        cls,
        coords: np.ndarray,
        visibility: np.ndarray,
        presence: np.ndarray,
        timestamp_ms: int,
    ) -> Pose:
        landmarks = [
            Landmark(
                x=coords[i, 0],
                y=coords[i, 1],
                z=coords[i, 2],
                visibility=float(visibility[i]),
                presence=float(presence[i]),
            )
            for i in range(33)
        ]

        return Pose(landmarks=landmarks, timestamp_ms=timestamp_ms)
