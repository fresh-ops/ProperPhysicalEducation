from typing import NamedTuple, Tuple

class Pose(NamedTuple):
    """
        Класс эталлонной позы. Содержит в себе информацию об эталонных углах в конечностях для конкретной позы, а также допустимое отклонение.

        Fields:
            name (str): имя позы
            threshold (float): допустимое отклонение
            left_shoulder_angle (float): угол в левом плече
            right_shoulder_angle (float): угол в правом плече
            left_elbow_angle (float): угол в левом локте
            right_elbow_angle (float): угол в правом локте
            left_knee_angle (float): угол в левом колене
            right_knee_angle (float): угол в правом колене
    """
    name: str
    threshold: float

    left_shoulder_angle: float
    right_shoulder_angle: float
    left_elbow_angle: float
    right_elbow_angle: float
    left_knee_angle: float
    right_knee_angle: float

    def get_angles_list(self) -> Tuple:
        """
            Возвращает кортеж углов в конечностях

            Returns:
                Tuple[float]: список позиционных углов в конечностях
        """
        return self[2:]

    def __eq__(self, other) -> bool:
        if not isinstance(other, Pose):
            return False

        threshold = self.threshold + other.threshold
        for first_angle, second_angle in zip(self.get_angles_list(), other.get_angles_list()):
            if abs(first_angle - second_angle) > threshold:
                return False

        return True

