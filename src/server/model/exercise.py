from typing import NamedTuple
from model.pose import Pose


class Exercise(NamedTuple):
    """
    Класс упражнения. Содержит в себе информацию об упражнении, а также эталонные позы для этого упражнения.

    Fields:
        id (int): идентификатор упражнения
        name (str): имя упражнения
        poses (list[Pose]): список эталонных поз для этого упражнения
    """

    id: int
    name: str
    poses: list[Pose]
