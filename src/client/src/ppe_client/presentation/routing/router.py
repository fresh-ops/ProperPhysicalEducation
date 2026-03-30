from PySide6 import QtCore, QtWidgets


class Router(QtCore.QObject):
    """
    Application routing system.
    """

    _stack: QtWidgets.QStackedWidget

    def __init__(
        self, stack: QtWidgets.QStackedWidget, parent: QtCore.QObject | None = None
    ) -> None:
        super().__init__(parent)

        self._stack = stack
