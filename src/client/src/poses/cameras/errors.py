class CameraServiceError(Exception):
    """Base class for exceptions in this module."""

    pass


class CameraNotFoundError(CameraServiceError):
    """Exception raised when a camera is not found."""

    def __init__(self, camera_index: int) -> None:
        self.message = f"Camera with index {camera_index} not found."
        super().__init__(self.message)


class CameraServiceDoubleInstanceError(CameraServiceError):
    """Exception raised when trying to create a second instance of CameraService."""

    def __init__(self) -> None:
        self.message = "CameraService is a singleton and cannot be instantiated more"
        "than once. Use CameraService.get_instance() to get the single instance of this"
        " class."
        super().__init__(self.message)
