from PySide6 import QtWidgets

from .payload import Payload
from .view_model import ViewModel


class Screen[P: Payload, VM: ViewModel](QtWidgets.QWidget):
    """
    Base screen class.
    """

    _view_model: VM

    def __init__(self, view_model: VM, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._view_model = view_model

    def on_create(self) -> None:
        """
        Lifecycle method called once, when the screen is created.
        """
        pass

    def on_enter(self, payload: P | None = None) -> None:
        """
        Lifecycle method called everytime the screen becomes visible to the user.
        """
        pass

    def on_leave(self) -> None:
        """
        Lifecycle method called everytime the screen becomes invisible to the user.
        """
        pass

    def on_destroy(self) -> None:
        """
        Lifecycle method called when the screen is about to be destroyed.
        """
        pass
