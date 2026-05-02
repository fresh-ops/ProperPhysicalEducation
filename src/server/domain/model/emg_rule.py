from dataclasses import dataclass

from domain.model.zone import Zone


@dataclass(frozen=True)
class EmgRule:
    target_zone: Zone
