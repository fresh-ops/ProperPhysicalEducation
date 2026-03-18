from collections.abc import Callable
from typing import Protocol

from ..cameras.frame import Frame


class CameraSession(Protocol):
    def attach(self, callback: Callable[[Frame], None]) -> None:
        """Attach the callback to the frame reading."""
        ...

    def detach(self, callback: Callable[[Frame], None]) -> None:
        """Dettach the callback from the frame reading."""
        ...

    def terminate(self) -> bool:
        """Terminate this session."""
        ...
