from typing import NamedTuple
from domain.model.pose import Pose
from domain.model.rule import Rule


class Exercise(NamedTuple):
    """
    Класс упражнения.

    Fields:
        id (int): идентификатор упражнения
        name (str): имя упражнения
        poses (list[Pose]): список эталонных поз для этого упражнения
        rules (list[Rule]): список правил для этого упражнения
    """

    id: int
    name: str
    poses: list[Pose]
    rules: list[Rule]
