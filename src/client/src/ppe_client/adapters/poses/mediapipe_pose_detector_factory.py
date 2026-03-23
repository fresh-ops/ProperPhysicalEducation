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

from .mediapipe_pose_detector import MediaPipePoseDetector

_MODEL_ASSET_PATH = "assets/pose_landmarker.task"
_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"


class MediaPipePoseDetectorFactory:
    _model_path: Path

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[4]
        self._model_path = project_root / _MODEL_ASSET_PATH

    def create(self) -> MediaPipePoseDetector:
        if not self._is_model_loaded():
            self._load_model()

        base_options = BaseOptions(model_asset_path=str(self._model_path))
        options = PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionTaskRunningMode.VIDEO,
            output_segmentation_masks=True,
        )

        pose_landmarker = PoseLandmarker.create_from_options(options)
        return MediaPipePoseDetector(pose_landmarker)

    def _is_model_loaded(self) -> bool:
        return self._model_path.is_file() and self._model_path.stat().st_size > 0

    def _load_model(self) -> None:
        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(_MODEL_URL, timeout=20) as response:
            response.raise_for_status()
            with open(self._model_path, "wb") as model_file:
                model_file.write(response.content)
