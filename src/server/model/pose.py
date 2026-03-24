from typing import NamedTuple, Tuple

from analyzer.pose.skeleton_transformer.skeleton import Angle


class Pose(NamedTuple):
    """
    Класс эталлонной позы. Содержит в себе информацию об эталонных углах в конечностях для конкретной позы, а также допустимое отклонение.

    Fields:
        id (int): идентификатор позы
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

    id: int
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

    def get_angles_list(self) -> list[float]:
        """
        Возвращает кортеж углов в конечностях

        Returns:
            List[float]: список позиционных углов в конечностях
        """
        return [
            self.left_shoulder_angle,
            self.right_shoulder_angle,
            self.left_elbow_angle,
            self.right_elbow_angle,
            self.left_knee_angle,
            self.right_knee_angle,
            self.left_hip_angle,
            self.right_hip_angle,
        ]

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
            Angle.LEFT_SHOULDER: self.left_shoulder_angle,
            Angle.RIGHT_SHOULDER: self.right_shoulder_angle,
            Angle.LEFT_ELBOW: self.left_elbow_angle,
            Angle.RIGHT_ELBOW: self.right_elbow_angle,
            Angle.LEFT_KNEE: self.left_knee_angle,
            Angle.RIGHT_KNEE: self.right_knee_angle,
            Angle.LEFT_HIP: self.left_hip_angle,
            Angle.RIGHT_HIP: self.right_hip_angle,
        }
