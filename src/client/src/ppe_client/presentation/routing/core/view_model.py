from typing import TYPE_CHECKING

from PySide6 import QtCore

from .payload import Payload

if TYPE_CHECKING:
    from .route import RouteName


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

    def request_navigation(self, route: "RouteName", payload: Payload) -> None:
        """
        Request navigation to the specified route.
        """
        self.navigation_requested.emit(route, payload)
