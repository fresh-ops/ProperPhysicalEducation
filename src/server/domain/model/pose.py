from dataclasses import dataclass
from typing import Tuple

from domain.model.angle import Angle


@dataclass(frozen=True)
class Pose:
    """
    Класс эталлонной позы. Содержит в себе информацию об эталонных углах в конечностях для конкретной позы, а также допустимое отклонение.

    Fields:
        id (str): идентификатор позы
        name (str): имя позы
        threshold (float): допустимое отклонение
        left_shoulder_angle (float): угол в левом плече
        right_shoulder_angle (float): угол в правом плече
        left_elbow_angle (float): угол в левом локте
        right_elbow_angle (float): угол в правом локте
        left_knee_angle (float): угол в левом колене
        right_knee_angle (float): угол в правом колене
        left_hip_angle (float): угол в левом бедре
        right_hip_angle (float): угол в правом бедре
    """

    id: str
    name: str
    threshold: float

    left_shoulder_angle: float
    right_shoulder_angle: float
    left_elbow_angle: float
    right_elbow_angle: float
    left_knee_angle: float
    right_knee_angle: float
    left_hip_angle: float
    right_hip_angle: float

    def __post_init__(self) -> None:
        self._validate_id()
        self._validate_name()
        self._validate_threshold()
        self._validate_angles()

    def get_angles_list(self) -> list[float]:
        """
        Возвращает список углов в конечностях

        Returns:
            List[float]: список позиционных углов в конечностях
        """
        return list(self.angles.values())

    def get_angle_ranges(self) -> dict[Angle, Tuple[float, float]]:
        """
        Возвращает словарь с диапазонами допустимых значений углов.

        Returns:
            Dict[Angle, Tuple[float, float]]: словарь с диапазонами углов
        """
        ranges = {}

        for angle, angle_value in self.angles.items():
            ranges[angle] = (angle_value - self.threshold, angle_value + self.threshold)

        return ranges

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pose):
            return False

        threshold = self.threshold + other.threshold
        for first_angle, second_angle in zip(
            self.get_angles_list(), other.get_angles_list()
        ):
            if abs(first_angle - second_angle) > threshold:
                return False

        return True

    @property
    def angles(self) -> dict[Angle, float]:
        return {
            angle_member: getattr(self, angle_member.field_name)
            for angle_member in Angle
        }

    def _validate_id(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError(f"id must be str, got {type(self.id).__name__}")

    def _validate_name(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError(f"name must be str, got {type(self.name).__name__}")

    def _validate_threshold(self) -> None:
        if not isinstance(self.threshold, (int, float)):
            raise TypeError(
                f"threshold must be numeric, got {type(self.threshold).__name__}"
            )
        if self.threshold < 0:
            raise ValueError("threshold must be non-negative")

    def _validate_angles(self) -> None:
        for angle_name in Angle.get_all_field_names():
            value = getattr(self, angle_name)
            if value is None:
                continue
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"{angle_name} must be numeric, got {type(value).__name__}"
                )
            if not (0 <= value <= 180):
                raise ValueError(f"{angle_name} must be in range [0, 180], got {value}")
