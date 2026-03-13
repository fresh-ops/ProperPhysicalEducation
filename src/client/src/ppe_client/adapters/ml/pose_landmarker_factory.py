from pathlib import Path

import mediapipe as mp
import requests
from cv2.typing import MatLike
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)
from mediapipe.tasks.python.vision.pose_landmarker import (
    PoseLandmarker,
    PoseLandmarkerOptions,
)

MODEL_ASSET_PATH = "assets/pose_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"


class MediaPipePoseDetector:
    """Adapter that hides MediaPipe image conversion from application layer."""

    def __init__(self, pose_landmarker: PoseLandmarker) -> None:
        self._pose_landmarker = pose_landmarker

    def detect_for_video_frame(self, frame: MatLike, timestamp_ms: int) -> object:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        return self._pose_landmarker.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        self._pose_landmarker.close()


def get_model_asset_path() -> Path:
    project_root = Path(__file__).resolve().parents[4]
    return project_root / MODEL_ASSET_PATH


def is_model_file_loaded(model_path: Path) -> bool:
    return model_path.is_file() and model_path.stat().st_size > 0


def load_model_file(model_path: Path) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(MODEL_URL, timeout=20) as response:
        response.raise_for_status()
        with open(model_path, "wb") as model_file:
            model_file.write(response.content)


def create_video_pose_landmarker() -> MediaPipePoseDetector:
    model_path = get_model_asset_path()
    if not is_model_file_loaded(model_path):
        load_model_file(model_path)

    base_options = BaseOptions(model_asset_path=str(model_path))
    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionTaskRunningMode.VIDEO,
        output_segmentation_masks=True,
    )

    pose_landmarker = PoseLandmarker.create_from_options(options)
    return MediaPipePoseDetector(pose_landmarker)
