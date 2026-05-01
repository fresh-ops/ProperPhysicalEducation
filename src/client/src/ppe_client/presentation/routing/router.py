import asyncio
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
    _view_models: dict[type[ViewModel[Any]], ViewModel[Any]]
    _enter_task: asyncio.Task[None] | None = None

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
        self._view_models = {}

    @QtCore.Slot(object, object)
    def navigate_by_name(self, route_name: RouteName, payload: Payload) -> None:
        if route_name not in self._scheme:
            raise RouteNotFoundError(route_name)
        print(f"Navigating to {route_name}")
        self.navigate_to(self._scheme[route_name], payload)

    @QtCore.Slot(object, object)
    def navigate_to[P: Payload](self, route: RouteDescriptor[P], payload: P) -> None:
        """
        Navigate to the specified route.
        """
        self._validate_payload(route.payload, payload)

        if route.view_model in self._view_models:
            view_model = self._view_models[route.view_model]
        else:
            view_model = self._screen_factory._container.get(route.view_model)
            self._view_models[route.view_model] = view_model

        screen = route.screen(view_model=view_model)
        self._bind_navigation(view_model)

        loop = asyncio.get_running_loop()
        self._enter_task = loop.create_task(view_model.on_enter(payload=payload))
        screen.setParent(self._stack)

        previous_widget = self._stack.currentWidget()
        if isinstance(previous_widget, Screen):
            self._unbind_navigation(previous_widget._view_model)
            previous_widget._view_model.setParent(None)

        self._stack.addWidget(screen)
        self._stack.setCurrentWidget(screen)
        if previous_widget is not None:
            self._stack.removeWidget(previous_widget)
            previous_widget.close()
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
