from typing import override

from PySide6 import QtCore, QtGui, QtWidgets

from ppe_client.adapters.cameras import (
    RefCountedCameraSessionStorage,
    SessionTerminator,
)
from ppe_client.adapters.cameras.open_cv import (
    OpenCVCameraEnumerator,
    OpenCVCameraSessionFactory,
)
from ppe_client.adapters.network import ExerciseSession
from ppe_client.adapters.poses import MediaPipePoseDetectorFactory
from ppe_client.adapters.poses.restoration import PoseRestorer
from ppe_client.application.cameras import CameraSessionService
from ppe_client.application.poses import PoseService

from .routing import Route
from .routing.router import Router
from .screens.cameras_screen import CamerasPayload, CamerasScreen
from .screens.my_screen import MyScreen, MyScreenPayload


class MainWindow(QtWidgets.QMainWindow):
    _stack_widget: QtWidgets.QStackedWidget
    _router: Router

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PPE")

        self._stack_widget = QtWidgets.QStackedWidget()

        container = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(self._stack_widget)

        self.setCentralWidget(container)
        self.resize(800, 600)
        QtCore.QTimer.singleShot(0, self._setup_services)

    def _initialize_routing(self) -> None:
        self._router = Router(
            stacked_widget=self._stack_widget,
            scheme={
                Route.HOME: (MyScreen, MyScreenPayload),
                Route.CAMERAS: (
                    lambda **kwargs: CamerasScreen(
                        camera_enumerator=self._camera_enumerator,
                        pose_service=self._pose_service,
                        session_service=self._camera_session_service,
                        exercise_session=self._exercise_session,
                        **kwargs,
                    ),
                    CamerasPayload,
                ),
            },
            parent=self,
        )

        self._router.navigate_to(Route.CAMERAS, CamerasPayload(exercise_id=1))

    def _setup_services(self) -> None:
        self._camera_enumerator = OpenCVCameraEnumerator()
        self._session_terminator = SessionTerminator()
        self._camera_session_service = CameraSessionService(
            RefCountedCameraSessionStorage(self._session_terminator),
            OpenCVCameraSessionFactory(),
        )
        self._detector_factory = MediaPipePoseDetectorFactory()
        self._exercise_session = ExerciseSession()
        self._pose_service = PoseService(
            self._detector_factory, PoseRestorer(self._exercise_session, parent=self)
        )
        self._initialize_routing()

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Stop all capture sessions before window closes."""
        super().closeEvent(event)
