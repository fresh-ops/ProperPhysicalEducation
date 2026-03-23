from typing import Protocol

from .pose_detector import PoseDetector


class PoseDetectorFactory(Protocol):
    """Port that creates a pose detector instance for worker runtime."""

    def create(self) -> PoseDetector: ...
