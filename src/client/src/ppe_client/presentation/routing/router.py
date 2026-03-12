from typing import Any

from PySide6 import QtCore, QtWidgets

from .errors import DuplicateRouteError, InvalidPayloadError, RouteNotFoundError
from .payload import Payload
from .route import Route
from .screen import Screen
from .transition import Transition


class Router(QtCore.QObject):
    _stacked_widget: QtWidgets.QStackedWidget

    _routes: dict[Route, Transition]
    _payload_types: dict[Route, type[Payload]]

    _widgets: dict[Route, Screen[Any]]
    _current_route: Route | None

    def __init__(
        self,
        stacked_widget: QtWidgets.QStackedWidget,
        scheme: dict[Route, tuple[Transition, type[Payload]]],
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._stacked_widget = stacked_widget
        self._routes = {route: factory for route, (factory, _) in scheme.items()}
        self._payload_types = {
            route: payload_type for route, (_, payload_type) in scheme.items()
        }
        self._widgets = {}
        self._current_route = None

    def add_route(
        self,
        route: Route,
        transition: Transition,
        payload_type: type[Payload],
    ) -> None:
        if route in self._routes:
            raise DuplicateRouteError(route)
        self._routes[route] = transition
        self._payload_types[route] = payload_type

    def navigate_to(self, route: Route, payload: Payload | None = None) -> None:
        if route not in self._routes:
            raise RouteNotFoundError(route)

        self._validate_payload_type(route, payload)

        if route in self._widgets and not self._widgets[route].is_reentrant():
            self._invalidate_widget_at(route)

        widget = self._get_widget_for(route)
        previous_widget = self._stacked_widget.currentWidget()

        self._current_route = route
        self._stacked_widget.setCurrentWidget(self._widgets[route])
        widget.on_enter(payload)
        if previous_widget and isinstance(previous_widget, Screen):
            previous_widget.on_leave()

    def _validate_payload_type(self, route: Route, payload: Payload | None) -> None:
        expected_payload_type = self._payload_types.get(route)
        if (
            expected_payload_type is not None
            and payload is not None
            and not isinstance(payload, expected_payload_type)
        ):
            raise InvalidPayloadError(route, expected_payload_type, type(payload))

    def _get_widget_for(self, route: Route) -> Screen[Any]:
        if route in self._widgets:
            return self._widgets[route]
        return self._create_widget_for(route)

    def _bind_navigation(self, widget: Screen[Any]) -> None:
        widget.navigation_requested.connect(self._on_navigation_requested)

    @QtCore.Slot(object, object)
    def _on_navigation_requested(
        self,
        route: Route,
        payload: Payload | None = None,
    ) -> None:
        self.navigate_to(route, payload)

    def _invalidate_widget_at(self, route: Route) -> None:
        widget = self._widgets.pop(route)
        widget.navigation_requested.disconnect(self._on_navigation_requested)
        self._stacked_widget.removeWidget(widget)
        widget.deleteLater()

    def _create_widget_for(self, route: Route) -> Screen[Any]:
        widget = self._routes[route]()
        self._widgets[route] = widget
        self._stacked_widget.addWidget(widget)
        self._bind_navigation(widget)
        return widget
