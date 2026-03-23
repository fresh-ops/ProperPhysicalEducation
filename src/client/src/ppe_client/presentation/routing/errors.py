from .payload import Payload
from .route import Route


class RouterError(Exception):
    pass


class DuplicateRouteError(RouterError):
    def __init__(self, route: Route) -> None:
        super().__init__(f"Route '{route}' already exists in scheme")


class RouteNotFoundError(RouterError):
    def __init__(self, route: Route) -> None:
        super().__init__(f"Route '{route}' not found in scheme")


class InvalidPayloadError(RouterError):
    def __init__(
        self,
        route: Route,
        expected_payload_type: type[Payload],
        actual_payload_type: type[Payload],
    ) -> None:
        super().__init__(
            f"Route '{route}' expects payload '{expected_payload_type.__name__}', "
            f"got '{actual_payload_type.__name__}'"
        )
