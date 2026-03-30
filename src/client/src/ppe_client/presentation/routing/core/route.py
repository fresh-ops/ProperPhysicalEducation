from dataclasses import dataclass

from .payload import Payload
from .screen import Screen
from .view_model import ViewModel


@dataclass(frozen=True, slots=True)
class Route[P: "Payload"]:
    """
    Navigation route.
    """

    name: str
    payload: type[P]
    view_model: type[ViewModel[P]]
    screen: type[Screen[ViewModel[P]]]
