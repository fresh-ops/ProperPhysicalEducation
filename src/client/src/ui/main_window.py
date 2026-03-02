from PySide6 import QtWidgets

from ui.my_screen import MyScreen, MyScreenPayload
from ui.routing import Route
from ui.routing.router import Router


class MainWindow(QtWidgets.QMainWindow):
    _stack_widget: QtWidgets.QStackedWidget
    _router: Router

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("My Best App")

        self._stack_widget = QtWidgets.QStackedWidget()

        container = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(self._stack_widget)

        self.setCentralWidget(container)

        self._router = Router(
            stacked_widget=self._stack_widget,
            scheme={
                Route.HOME: (MyScreen, MyScreenPayload),
            },
            parent=self,
        )

        self._router.navigate_to(Route.HOME, MyScreenPayload(label="Hell"))
