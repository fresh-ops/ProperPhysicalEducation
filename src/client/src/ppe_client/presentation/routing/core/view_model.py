from PySide6 import QtCore

from .payload import Payload
from .route import Route


class ViewModel[P: Payload](QtCore.QObject):
    """
    Base view model class.
    """

    navigation_requested = QtCore.Signal(object, object)

    def on_enter(self, payload: P | None = None) -> None:
        """
        Lifecycle method called every time the router navigates to this view model.
        """
        pass

    def request_navigation[R: Payload](self, route: Route[R], payload: R) -> None:
        self.navigation_requested.emit(route, payload)
