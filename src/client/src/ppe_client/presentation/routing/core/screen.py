from typing import Any, override

from PySide6 import QtGui, QtWidgets

from .view_model import ViewModel


class Screen[VM: ViewModel[Any]](QtWidgets.QWidget):
    """
    Base screen class.
    """

    _view_model: VM

    def __init__(self, view_model: VM, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._view_model = view_model
        self._view_model.setParent(self)
        self.on_create()

    def on_create(self) -> None:
        """
        Lifecycle method called once, when the screen is created.
        """
        pass

    def on_enter(self) -> None:
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

    @override
    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)

        if self.isVisible():
            self.on_enter()

    @override
    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        super().hideEvent(event)
        self.on_leave()

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.on_destroy()
        super().closeEvent(event)
