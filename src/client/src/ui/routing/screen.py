from PySide6 import QtCore, QtWidgets

from .payload import Payload
from .route import Route


class Screen[P: Payload](QtWidgets.QWidget):
    navigation_requested = QtCore.Signal(object, object)

    def request_navigation(
        self,
        route: Route,
        payload: Payload | None = None,
    ) -> None:
        self.navigation_requested.emit(route, payload)

    def is_reentrant(self) -> bool:
        return False

    def on_enter(self, payload: P | None = None) -> None:
        pass

    def on_leave(self) -> None:
        pass
