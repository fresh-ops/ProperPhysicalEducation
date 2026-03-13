from typing import Protocol

from cv2.typing import MatLike


class PoseDetector(Protocol):
    """Minimal pose detector contract used by pose capture worker."""

    def detect_for_video_frame(self, frame: MatLike, timestamp_ms: int) -> object: ...

    def close(self) -> None: ...


class PoseLandmarkerFactory(Protocol):
    """Port that creates a pose detector instance for worker runtime."""

    def __call__(self) -> PoseDetector: ...
