from PySide6 import QtCore, QtWidgets

from .routing import Router


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for PPE client.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PPE")
        self.resize(800, 600)
        QtCore.QTimer.singleShot(0, self._setup_ui)

    def _setup_ui(self) -> None:
        """Initializes the UI."""
        self._stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        self._router = Router(self._stacked_widget, self)
