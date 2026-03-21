import numpy as np
from mediapipe.tasks.python.vision.drawing_styles import (
    get_default_pose_landmarks_style,
)
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec, draw_landmarks
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarksConnections,
)

from ppe_client.application.cameras import Frame
from ppe_client.application.poses import Pose

from ..cameras.frame_converter import FrameConverter
from .pose_converter import PoseConverter


class LandmarksDrawer:
    @classmethod
    def draw(cls, pose: Pose, frame: Frame) -> Frame:
        landmarks = PoseConverter.to_mediapipe(pose)
        image = np.copy(FrameConverter.to_ndarray(frame))

        landmark_style = get_default_pose_landmarks_style()
        connection_style = DrawingSpec(color=(0, 255, 0), thickness=2)

        draw_landmarks(
            image=image,
            landmark_list=landmarks,
            connections=PoseLandmarksConnections.POSE_LANDMARKS,
            landmark_drawing_spec=landmark_style,
            connection_drawing_spec=connection_style,
        )

        return Frame(
            raw=image.data.tobytes(),
            shape=frame.shape,
            timestamp_ms=frame.timestamp_ms,
            origin=frame.origin,
        )
