from dataclasses import dataclass

from .payload import Payload
from .screen import Screen
from .view_model import ViewModel

type RouteName = str
"""
Navigation route name.
"""


@dataclass(frozen=True, slots=True)
class RouteDescriptor[P: "Payload"]:
    """
    Navigation route descriptor.
    """

    payload: type[P]
    view_model: type[ViewModel[P]]
    screen: type[Screen[ViewModel[P]]]
