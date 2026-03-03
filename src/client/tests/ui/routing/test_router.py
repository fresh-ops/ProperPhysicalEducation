from unittest.mock import MagicMock

import pytest
from PySide6 import QtWidgets
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from src.ui.routing import (
    DuplicateRouteError,
    InvalidPayloadError,
    Payload,
    Route,
    RouteNotFoundError,
    Router,
    Screen,
    Transition,
)


@pytest.fixture
def stacked_widget(qtbot: QtBot) -> QtWidgets.QStackedWidget:
    widget = QtWidgets.QStackedWidget()
    qtbot.addWidget(widget)
    return widget


def test_add_duplicate_route_fails(stacked_widget: QtWidgets.QStackedWidget) -> None:
    router = Router(
        stacked_widget,
        {
            Route.HOME: (MagicMock(spec=Transition), Payload),
        },
    )
    with pytest.raises(
        DuplicateRouteError, match="Route 'home' already exists in scheme"
    ):
        router.add_route(Route.HOME, MagicMock(spec=Transition), Payload)


def test_navigate_to_unregistered_route_fails(
    stacked_widget: QtWidgets.QStackedWidget,
) -> None:
    router = Router(stacked_widget, {})
    with pytest.raises(RouteNotFoundError, match="Route 'home' not found in scheme"):
        router.navigate_to(Route.HOME)


def test_navigate_to_with_invalid_payload_type_fails(
    stacked_widget: QtWidgets.QStackedWidget,
) -> None:
    class ExpectedPayload(Payload):
        pass

    class ActualPayload(Payload):
        pass

    router = Router(
        stacked_widget,
        {
            Route.HOME: (MagicMock(spec=Transition), ExpectedPayload),
        },
    )

    with pytest.raises(
        InvalidPayloadError,
        match="Route 'home' expects payload 'ExpectedPayload', got 'ActualPayload'",
    ):
        router.navigate_to(Route.HOME, ActualPayload())


def test_navigate_to_valid_route_changes_screen(
    mocker: MockerFixture,
    stacked_widget: QtWidgets.QStackedWidget,
) -> None:
    class FakeScreen(Screen[Payload]):
        pass

    screen = FakeScreen()
    spy_screen = mocker.spy(screen, "on_enter")
    transition = MagicMock(spec=Transition, return_value=screen)

    router = Router(
        stacked_widget,
        {
            Route.HOME: (transition, Payload),
        },
    )
    router.navigate_to(Route.HOME, Payload())

    assert stacked_widget.currentWidget() is screen
    transition.assert_called_once()
    spy_screen.assert_called_once_with(Payload())
