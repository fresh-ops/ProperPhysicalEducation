from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from ppe_client.application.poses import Pose


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
