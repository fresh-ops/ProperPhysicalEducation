from typing import override

from PySide6 import QtGui, QtWidgets

from ppe_client.poses.cameras import CameraService
from ppe_client.poses.capturing import PoseCaptureOrchestrator

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

        self._setup_services()

        self._stack_widget = QtWidgets.QStackedWidget()

        container = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(self._stack_widget)

        self.setCentralWidget(container)

        self._router = Router(
            stacked_widget=self._stack_widget,
            scheme={
                Route.HOME: (MyScreen, MyScreenPayload),
                Route.CAMERAS: (
                    lambda **kwargs: CamerasScreen(
                        camera_service=self._camera_service,
                        capture_orchestrator=self._pose_capture_orchestrator,
                        **kwargs,
                    ),
                    CamerasPayload,
                ),
            },
            parent=self,
        )

        self._router.navigate_to(Route.CAMERAS, CamerasPayload())

    def _setup_services(self) -> None:
        self._camera_service = CameraService()
        self._pose_capture_orchestrator = PoseCaptureOrchestrator(
            self._camera_service, parent=self
        )

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Stop all capture sessions before window closes."""
        self._pose_capture_orchestrator.shutdown()
        super().closeEvent(event)
