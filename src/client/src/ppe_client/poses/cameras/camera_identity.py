from cv2_enumerate_cameras.camera_info import CameraInfo

type CameraKey = tuple[int, int]


def camera_key(camera_info: CameraInfo) -> CameraKey:
    """Return a stable identity key for a camera descriptor.

    Args:
        camera_info (CameraInfo): Camera descriptor from the camera service.

    Returns:
        CameraKey: Tuple of backend and index uniquely identifying the camera.
    """
    return (camera_info.backend, camera_info.index)
