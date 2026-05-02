from abc import ABC
from dataclasses import dataclass


@dataclass
class Rule(ABC):
    message: str
