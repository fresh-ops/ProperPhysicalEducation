from pathlib import Path

import requests
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


def get_model_asset_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return project_root / MODEL_ASSET_PATH


def is_model_file_loaded(model_path: Path) -> bool:
    return model_path.is_file() and model_path.stat().st_size > 0


def load_model_file(model_path: Path) -> None:
    response = requests.get(MODEL_URL)
    response.raise_for_status()

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        f.write(response.content)


def create_video_pose_landmarker() -> PoseLandmarker:
    model_path = get_model_asset_path()
    if not is_model_file_loaded(model_path):
        load_model_file(model_path)

    base_options = BaseOptions(model_asset_path=str(model_path))
    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionTaskRunningMode.VIDEO,
        output_segmentation_masks=True,
    )

    return PoseLandmarker.create_from_options(options)
