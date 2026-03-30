from typing import Any

from PySide6 import QtCore, QtWidgets

from .core import Payload, RouteDescriptor, RouteName, Screen, ViewModel
from .errors import InvalidPayloadError, RouteNotFoundError
from .screen_factory import ScreenFactory


class Router(QtCore.QObject):
    """
    Application routing system.
    """

    _stack: QtWidgets.QStackedWidget
    _screen_factory: ScreenFactory
    _scheme: dict[RouteName, RouteDescriptor[Any]]

    def __init__(
        self,
        stack: QtWidgets.QStackedWidget,
        screen_factory: ScreenFactory,
        scheme: dict[RouteName, RouteDescriptor[Any]],
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self._stack = stack
        self._screen_factory = screen_factory
        self._scheme = scheme

    @QtCore.Slot(object, object)
    def navigate_by_name(self, route_name: RouteName, payload: Payload) -> None:
        if route_name not in self._scheme:
            raise RouteNotFoundError(route_name)
        self.navigate_to(self._scheme[route_name], payload)

    @QtCore.Slot(object, object)
    def navigate_to[P: Payload](self, route: RouteDescriptor[P], payload: P) -> None:
        """
        Navigate to the specified route.
        """
        self._validate_payload(route.payload, payload)
        screen, view_model = self._screen_factory.create(route)
        self._bind_navigation(view_model)

        view_model.on_enter(payload=payload)
        screen.setParent(self._stack)

        previous_widget = self._stack.currentWidget()
        if isinstance(previous_widget, Screen):
            self._unbind_navigation(previous_widget._view_model)

        self._stack.removeWidget(previous_widget)
        self._stack.setCurrentWidget(screen)
        previous_widget.deleteLater()

    def _validate_payload[P: Payload, Q: Payload](
        self, expected_type: type[P], payload: Q
    ) -> None:
        """
        Validate the payload type.
        """
        if not isinstance(payload, expected_type):
            raise InvalidPayloadError(expected_type, type(payload))

    def _bind_navigation[P: Payload](self, view_model: ViewModel[P]) -> None:
        """
        Bind the navigation request handler.
        """
        view_model.navigation_requested.connect(self.navigate_by_name)

    def _unbind_navigation[P: Payload](self, view_model: ViewModel[P]) -> None:
        """
        Unbind the navigation request handler.
        """
        view_model.navigation_requested.disconnect(self.navigate_by_name)
