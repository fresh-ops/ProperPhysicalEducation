from cv2 import VideoCapture

from ppe_client.domain import CameraDescriptor

from .open_cv_camera_session import OpenCVCameraSession


class OpenCVCameraSessionFactory:
    def create_for(self, camera: CameraDescriptor) -> OpenCVCameraSession:
        capture = VideoCapture(camera.index, camera.backend)
        return OpenCVCameraSession(capture)
