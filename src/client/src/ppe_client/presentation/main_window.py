from PySide6 import QtCore, QtWidgets
from wireup import SyncContainer, create_sync_container

from .routing import Router, ScreenFactory


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for PPE client.
    """

    _services: SyncContainer

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PPE")
        self.resize(800, 600)
        self._services = create_sync_container()
        QtCore.QTimer.singleShot(0, self._setup_ui)

    def _setup_ui(self) -> None:
        """Initializes the UI."""
        self._stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        screen_factory = ScreenFactory(self._services)
        self._router = Router(
            self._stacked_widget,
            screen_factory,
            {},
            self,
        )
