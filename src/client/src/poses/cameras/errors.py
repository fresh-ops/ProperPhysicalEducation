class CameraServiceError(Exception):
    """Base class for exceptions in this module."""

    pass


class CameraNotFoundError(CameraServiceError):
    """Exception raised when a camera is not found."""

    def __init__(self, camera_index: int) -> None:
        self.message = f"Camera with index {camera_index} not found."
        super().__init__(self.message)
