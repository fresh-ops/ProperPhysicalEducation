import asyncio
from typing import override

from PySide6 import QtCore, QtGui, QtWidgets
from qasync import QApplication
from wireup.ioc.container.sync_container import ScopedSyncContainer

from ppe_client.presentation.screens.choose_exercise.choose_exercise_payload import (
    ChooseExercisePayload,
)

from .routing import Router, Routes, ScreenFactory
from .screens.choose_exercise import (
    choose_exercise_route_descriptor,
)
from .screens.sensor_calibration import (
    sensor_calibration_route_descriptor,
)
from .screens.sensor_connection import (
    sensor_connection_route_descriptor,
)
from .screens.sensor_discovery import (
    sensor_discovery_route_descriptor,
)
from .screens.training import (
    training_route_descriptor,
)


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for PPE client.
    """

    _container: ScopedSyncContainer

    def __init__(
        self, container: ScopedSyncContainer, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("PPE")
        self.resize(800, 600)
        self._container = container
        QtCore.QTimer.singleShot(0, self._setup_ui)

    @QtCore.Slot()
    def _setup_ui(self) -> None:
        """Initializes the UI."""
        self._stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        screen_factory = ScreenFactory(self._container)
        self._router = Router(
            self._stacked_widget,
            screen_factory,
            {
                Routes.CHOOSE_EXERCISE: choose_exercise_route_descriptor,
                Routes.SENSOR_DISCOVERY: sensor_discovery_route_descriptor,
                Routes.SENSOR_CONNECTION: sensor_connection_route_descriptor,
                Routes.SENSOR_CALIBRATION: sensor_calibration_route_descriptor,
                Routes.TRAINING: training_route_descriptor,
            },
            self,
        )

        self._router.navigate_by_name(Routes.CHOOSE_EXERCISE, ChooseExercisePayload())

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.ignore()
        asyncio.create_task(self.shutdown())

    async def shutdown(self) -> None:
        print("Shutdown")
        await self._router.shutdown()
        print("Quiting")
        app = QApplication.instance()
        if app is not None:
            app.exit(0)
        else:
            print("App is None")
