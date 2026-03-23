from collections.abc import Callable
from typing import Any

from .screen import Screen

type Transition = Callable[[], Screen[Any]]
