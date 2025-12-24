from enum import Enum


LANDMARKS_COUNT = 33
DIMENSIONS = 3


class Landmark(Enum):
    """
        Перечисление всех точек цифрового скелета. Каждой точке соответствует индекс в массиве,
        по которому лежит данная точка
    """
    NOSE = 0

    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3

    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6

    LEFT_EAR = 7
    RIGHT_EAR = 8

    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14

    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    LEFT_PINKY = 17
    RIGHT_PINKY = 18

    LEFT_INDEX = 19
    RIGHT_INDEX = 20

    LEFT_THUMB = 21
    RIGHT_THUMB = 22

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    LEFT_HEEL = 29
    RIGHT_HEEL = 30

    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

    @property
    def index(self):
        return self.value


class Angle(Enum):
    """
        Перечисление определений углов в конечностях. Каждому углу соответствует набор точек цифрового
        скелета типа Tuple[Landmark, Landmark, Landmark]. При этом средняя точка набора - вершина угла
    """
    LEFT_SHOULDER = (Landmark.LEFT_HIP, Landmark.LEFT_SHOULDER, Landmark.LEFT_ELBOW)
    RIGHT_SHOULDER = (Landmark.RIGHT_HIP, Landmark.RIGHT_SHOULDER, Landmark.RIGHT_ELBOW)

    LEFT_ELBOW = (Landmark.LEFT_SHOULDER, Landmark.LEFT_ELBOW, Landmark.LEFT_WRIST)
    RIGHT_ELBOW = (Landmark.RIGHT_SHOULDER, Landmark.RIGHT_ELBOW, Landmark.RIGHT_WRIST)

    LEFT_KNEE = (Landmark.LEFT_HIP, Landmark.LEFT_KNEE, Landmark.LEFT_ANKLE)
    RIGHT_KNEE = (Landmark.RIGHT_HIP, Landmark.RIGHT_KNEE, Landmark.RIGHT_ANKLE)

    @property
    def vertex(self):
        return self.value[1]

    @property
    def side_a(self):
        return self.value[0]

    @property
    def side_b(self):
        return self.value[2]
