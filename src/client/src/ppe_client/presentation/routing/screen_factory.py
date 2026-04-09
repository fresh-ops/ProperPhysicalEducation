from wireup.ioc.container.sync_container import ScopedSyncContainer 

from .core.payload import Payload
from .core.route import RouteDescriptor
from .core.screen import Screen
from .core.view_model import ViewModel


class ScreenFactory:
    """
    Factory for creating screens.
    """

    _container: ScopedSyncContainer

    def __init__(self, container: ScopedSyncContainer) -> None:
        self._container = container

    def create[P: Payload](
        self, route: RouteDescriptor[P]
    ) -> tuple[Screen[ViewModel[P]], ViewModel[P]]:
        """
        Creates a new screen with it's viewmodel based on the given route.
        """
        view_model = self._container.get(route.view_model)
        screen = route.screen(view_model=view_model)

        return screen, view_model
