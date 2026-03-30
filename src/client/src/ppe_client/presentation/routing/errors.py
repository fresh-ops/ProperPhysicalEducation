from .core import Payload


class RouterError(Exception):
    pass


class InvalidPayloadError(RouterError):
    def __init__(
        self,
        expected_payload_type: type[Payload],
        actual_payload_type: type[Payload],
    ) -> None:
        super().__init__(
            f"Route expected payload '{expected_payload_type.__name__}', but "
            f"got '{actual_payload_type.__name__}'"
        )
