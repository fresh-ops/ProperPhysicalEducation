from wireup import SyncContainer

from .core.payload import Payload
from .core.route import Route
from .core.screen import Screen
from .core.view_model import ViewModel


class ScreenFactory:
    """
    Factory for creating screens.
    """

    _services: SyncContainer

    def __init__(self, services: SyncContainer) -> None:
        self._services = services

    def create[P: Payload](
        self, route: Route[P]
    ) -> tuple[Screen[ViewModel[P]], ViewModel[P]]:
        """
        Creates a new screen with it's viewmodel based on the given route.
        """
        view_model = route.view_model._injected(services=self._services)
        screen = route.screen(view_model=view_model)

        return screen, view_model
