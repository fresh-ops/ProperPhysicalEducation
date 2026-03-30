from PySide6 import QtCore

from .payload import Payload


class ViewModel[P: Payload](QtCore.QObject):
    """
    Base view model class.
    """

    def on_enter(self, payload: P | None = None) -> None:
        """
        Lifecycle method called every time the router navigates to this view model.
        """
        pass
