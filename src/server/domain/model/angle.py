from enum import Enum

from domain.model.landmark import Landmark


class Angle(Enum):
    """
    Перечисление определений углов в конечностях. Каждому углу соответствует набор точек цифрового
    скелета типа Tuple[Landmark, Landmark, Landmark]. При этом средняя точка набора - вершина угла
    """

    LEFT_SHOULDER_ANGLE = (
        Landmark.LEFT_HIP,
        Landmark.LEFT_SHOULDER,
        Landmark.LEFT_ELBOW,
    )
    RIGHT_SHOULDER_ANGLE = (
        Landmark.RIGHT_HIP,
        Landmark.RIGHT_SHOULDER,
        Landmark.RIGHT_ELBOW,
    )

    LEFT_ELBOW_ANGLE = (
        Landmark.LEFT_SHOULDER,
        Landmark.LEFT_ELBOW,
        Landmark.LEFT_WRIST,
    )
    RIGHT_ELBOW_ANGLE = (
        Landmark.RIGHT_SHOULDER,
        Landmark.RIGHT_ELBOW,
        Landmark.RIGHT_WRIST,
    )

    LEFT_KNEE_ANGLE = (Landmark.LEFT_HIP, Landmark.LEFT_KNEE, Landmark.LEFT_ANKLE)
    RIGHT_KNEE_ANGLE = (Landmark.RIGHT_HIP, Landmark.RIGHT_KNEE, Landmark.RIGHT_ANKLE)

    LEFT_HIP_ANGLE = (Landmark.LEFT_SHOULDER, Landmark.LEFT_HIP, Landmark.LEFT_KNEE)
    RIGHT_HIP_ANGLE = (Landmark.RIGHT_SHOULDER, Landmark.RIGHT_HIP, Landmark.RIGHT_KNEE)

    @property
    def vertex(self) -> Landmark:
        return self.value[1]

    @property
    def side_a(self) -> Landmark:
        return self.value[0]

    @property
    def side_b(self) -> Landmark:
        return self.value[2]

    @property
    def field_name(self) -> str:
        return self.name.lower()

    @classmethod
    def get_all_field_names(cls) -> list[str]:
        return [member.name.lower() for member in cls]
