from .camera_descriptor import CameraDescriptor

type CameraKey = tuple[int, int]


def camera_key(camera: CameraDescriptor) -> CameraKey:
    """Return a stable identity key for a camera descriptor."""
    return (camera.backend, camera.index)
