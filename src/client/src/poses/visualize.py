import numpy as np
from cv2.typing import MatLike
from mediapipe.tasks.python.vision.drawing_styles import (
    get_default_pose_landmarks_style,
)
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec, draw_landmarks
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarkerResult,
    PoseLandmarksConnections,
)


def draw_landmarks_on_image(
    image: MatLike, detection_result: PoseLandmarkerResult
) -> MatLike:
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(image)

    pose_landmark_style = get_default_pose_landmarks_style()
    pose_connection_style = DrawingSpec(color=(0, 255, 0), thickness=2)

    for pose_landmarks in pose_landmarks_list:
        draw_landmarks(
            image=annotated_image,
            landmark_list=pose_landmarks,
            connections=PoseLandmarksConnections.POSE_LANDMARKS,
            landmark_drawing_spec=pose_landmark_style,
            connection_drawing_spec=pose_connection_style,
        )

    return annotated_image
