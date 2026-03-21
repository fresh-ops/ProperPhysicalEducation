import mediapipe as mp
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
)

from ppe_client.application.cameras import Frame
from ppe_client.application.poses import Landmark, Pose

from ..cameras.frame_converter import FrameConverter


class MediaPipePoseDetector:
    _pose_landmarker: PoseLandmarker

    def __init__(self, pose_landmarker: PoseLandmarker) -> None:
        self._pose_landmarker = pose_landmarker

    def detect(self, frame: Frame) -> Pose | None:
        image = FrameConverter.to_ndarray(frame)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        result = self._pose_landmarker.detect_for_video(
            mp_image, timestamp_ms=frame.timestamp_ms
        )
        if len(result.pose_landmarks) == 0:
            return None
        landmarks = [
            Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                presence=landmark.presence,
            )
            for landmark in result.pose_landmarks[0]
        ]

        return Pose(landmarks, frame.timestamp_ms)

    def close(self) -> None:
        self._pose_landmarker.close()
