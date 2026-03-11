from PySide6 import QtWidgets

from src.poses.cameras import CameraService

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
                    lambda **kwargs: CamerasScreen(self._camera_service, **kwargs),
                    CamerasPayload,
                ),
            },
            parent=self,
        )

        self._router.navigate_to(Route.CAMERAS, CamerasPayload())

    def _setup_services(self) -> None:
        self._camera_service = CameraService()
