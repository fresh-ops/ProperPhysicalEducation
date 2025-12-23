import math
from poses.pose import Pose
from skeleton import LANDMARKS_COUNT, Angle, Landmark

NUM_COORDINATES = 3  # Количество координатных осей для точки

CONNECTIONS = {
    # ГОЛОВА
    0: [2, 5],
    1: [2],
    2: [0, 1, 3, 7],
    3: [2],
    4: [5],
    5: [0, 4, 6, 8],
    6: [5],
    7: [2],
    8: [5],
    9: [10],
    10: [9],

    # ТЕЛО
    11: [12, 13, 23],
    12: [11, 14, 24],
    13: [11, 15],
    14: [12, 16],
    15: [13, 17, 19, 21],
    16: [14, 18, 20, 22],
    17: [15, 19],
    18: [16, 20],
    19: [15, 17],
    20: [16, 18],
    21: [15],
    22: [16],
    23: [11, 24, 25],
    24: [12, 23, 26],
    25: [23, 27],
    26: [24, 28],
    27: [25, 29, 31],
    28: [26, 30, 32],
    29: [27, 31],
    30: [28, 32],
    31: [27, 29],
    32: [28, 30]
}

class AngleAnalyzer:
    def __init__(self):
        self.points = [(0.0, 0.0, 0.0)] * LANDMARKS_COUNT
        self.angles = {}
        self.angle_history = {}

                
    def calculate_angle(self, angle: Angle):
        """
        Вычисляет угол в точке p2 между линиями p1-p2 и p3-p2
        В ПЛОСКОСТИ XY (плоская проекция, Z игнорируется)

        Args:
            p1_idx: индекс первой точки
            p2_idx: индекс центральной точки (вершина угла)
            p3_idx: индекс третьей точки

        Returns:
            float: угол в градусах (0-180)
        """
        p1_idx = angle.side_a.index
        p2_idx = angle.vertex.index
        p3_idx = angle.side_b.index

        p1 = self.points[p1_idx]
        p2 = self.points[p2_idx]
        p3 = self.points[p3_idx]

        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])


        v1_len = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_len = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if v1_len < 1e-6 or v2_len < 1e-6:

            return 0.0

        angle1 = math.atan2(v1[1], v1[0])
        angle2 = math.atan2(v2[1], v2[0])

        angle_diff = abs(angle1 - angle2)

        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff

        return math.degrees(angle_diff)

    def calculate_all_angles(self):
        """
        Вычисляет все углы между связанными точками скелета согласно конфигурации CONNECTIONS

        Returns:
            dict: словарь со всеми вычисленными углами, где ключ - кортеж (центральная_точка, точка1, точка2),
                  значение - словарь с данными угла (angle, points, center)
        """
        angles = {}

        for center_idx, connections in CONNECTIONS.items():
            if len(connections) >= 2:
                for i in range(len(connections)):
                    for j in range(i + 1, len(connections)):
                        p1_idx = connections[i]
                        p3_idx = connections[j]

                        key = (center_idx, p1_idx, p3_idx)

                        angle = self.calculate_angle(p1_idx, center_idx, p3_idx)

                        angles[key] = {
                            'angle': angle,
                            'points': (p1_idx, center_idx, p3_idx),
                            'center': center_idx
                        }

                        if key not in self.angle_history:
                            self.angle_history[key] = []
                        self.angle_history[key].append(angle)

                        if len(self.angle_history[key]) > 100:
                            self.angle_history[key] = self.angle_history[key][-100:]

        self.angles = angles
        return angles

    def get_current_pose(self) -> Pose:
        """
        Создает объект Pose с текущими вычисленными углами тела

        Вычисляет ключевые углы для определения позы:
        - Углы плеч (между рукой и туловищем)
        - Углы локтей (в локтевых суставах)
        - Углы коленей (в коленных суставах)

        Returns:
            Pose: объект позы с вычисленными углами, пустым именем и нулевым порогом
        """
        return Pose(
            name="",
            threshold=0.0,
            left_shoulder_angle=self.calculate_angle(Angle.LEFT_SHOULDER),
            right_shoulder_angle=self.calculate_angle(Angle.RIGHT_SHOULDER),
            left_elbow_angle=self.calculate_angle(Angle.LEFT_ELBOW),
            right_elbow_angle=self.calculate_angle(Angle.RIGHT_ELBOW),
            left_knee_angle=self.calculate_angle(Angle.LEFT_KNEE),
            right_knee_angle=self.calculate_angle(Angle.RIGHT_KNEE)
        )
