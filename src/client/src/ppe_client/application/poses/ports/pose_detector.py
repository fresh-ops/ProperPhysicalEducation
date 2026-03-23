from collections.abc import Callable
from typing import Protocol

from ...cameras.frame import Frame
from ..pose import Pose


class PoseDetector(Protocol):
    """Minimal pose detector contract."""

    def detect(
        self, frame: Frame, callback: Callable[[Pose | None, Frame], None]
    ) -> None: ...

    def close(self) -> None: ...
