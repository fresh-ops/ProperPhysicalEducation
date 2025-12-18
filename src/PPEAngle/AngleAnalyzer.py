import paho.mqtt.client as mqtt
import time
import math

# Константы программы
MQTT_BROKER = "127.0.0.1" # Адрес MQTT брокера
MQTT_PORT = 1883  # Порт MQTT брокера (стандартный порт Mosquitto)
MQTT_TOPIC = "skeleton/points" # Топик для получения данных цифрового скелета
NUM_POINTS = 33 # Количество точек цифрового скелета
NUM_COORDINATES = 3 # Количество координатных осей для точки

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

# Тестовые данные точек скелета
TEST_POINTS = [[0.43315500020981, -0.0152943963185, -0.2632532119751], [0.43837544322014, -0.0288357399404, -0.25472643971443], [0.44018724560738, -0.02777613699436, -0.25478649139404], [0.44174206256866, -0.02730458788574, -0.25488764047623], [0.43188095092773, -0.03020882792771, -0.24896182119846], [0.43000492453575, -0.02994019910693, -0.24898125231266], [0.425462692976, -0.03097759559751, -0.24906097352505], [0.44287496805191, -0.01171371527016, -0.17180027067661], [0.42263209819794, -0.01448221504688, -0.14335076510906], [0.4367758333683, 0.00794063229114, -0.22997109591961], [0.42992147803307, 0.0079760523513, -0.22199015319347], [0.49010851979256, 0.0824698060751, -0.12679269909859], [0.37098488211632, 0.08911731094122, -0.07078934460878], [0.58488857746124, 0.11992567777634, -0.11454445868731], [0.27745190262794, 0.14025191962719, -0.05331132933497], [0.60016947984695, 0.25467967987061, -0.19929271936417], [0.25376811623573, 0.27326548099518, -0.13382296264172], [0.60785180330276, 0.29535952210426, -0.22483088076115], [0.2478002011776, 0.3095595240593, -0.15743997693062], [0.5952211022377, 0.30095985531807, -0.25525739789009], [0.26456850767136, 0.31512799859047, -0.19594965875149], [0.59026581048965, 0.2884524166584, -0.21343928575516], [0.26832139492035, 0.3051677942276, -0.1530637294054], [0.47006577253342, 0.42289063334465, -0.02400427311659], [0.40914127230644, 0.42737093567848, 0.02383933775127], [0.47279506921768, 0.66256564855576, 0.0072748917155], [0.40681234002113, 0.66285884380341, 0.08179214596748], [0.47891816496849, 0.85358828306198, 0.28282409906387], [0.41997185349464, 0.84716606140137, 0.3296976685524], [0.47248408198357, 0.87171429395676, 0.30219614505768], [0.43049076199532, 0.87150430679321, 0.34742420911789], [0.48401069641113, 0.93488013744354, 0.15799953043461], [0.40908414125443, 0.9309133887291, 0.21493278443813]]



class AngleAnalyzer:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC):
        self.mqtt_broker = broker
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.points = [(0.0, 0.0, 0.0)] * NUM_POINTS
        self.angles = {} 
        self.angle_history = {} 
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_connected = False
        self.mqtt_subscribed = False
        self.mqtt_data_received = False
        self.mqtt_last_message_time = 0
        
        self.setup_mqtt_callbacks()

    def check_t_pose(self, shoulder_threshold=5, elbow_threshold=15):
        """
        Упрощенная проверка Т-позы (только по углам)
        
        Args:
            shoulder_threshold: допустимое отклонение от 90° для плеч
            elbow_threshold: допустимое отклонение от 180° для локтей
            
        Returns:
            dict: Результаты проверки с описанием и статусом
        """
        specific_angles = self.get_specific_angles()
        
        if not specific_angles:
            return {
                'is_t_pose': False,
                'reason': 'Нет данных об углах',
                'details': {}
            }
        
        left_shoulder_angle = specific_angles['left_shoulder']['angle']
        right_shoulder_angle = specific_angles['right_shoulder']['angle']
        left_elbow_angle = specific_angles['left_elbow']['angle']
        right_elbow_angle = specific_angles['right_elbow']['angle']
        
        
        is_left_shoulder_ok = abs(left_shoulder_angle - 90) <= shoulder_threshold
        is_right_shoulder_ok = abs(right_shoulder_angle - 90) <= shoulder_threshold
        is_left_elbow_ok = abs(left_elbow_angle - 180) <= elbow_threshold
        is_right_elbow_ok = abs(right_elbow_angle - 180) <= elbow_threshold
        

        shoulder_symmetry_ok = abs(left_shoulder_angle - right_shoulder_angle) <= 20
        elbow_symmetry_ok = abs(left_elbow_angle - right_elbow_angle) <= 20
        
        is_t_pose = (is_left_shoulder_ok and is_right_shoulder_ok and
                    is_left_elbow_ok and is_right_elbow_ok and
                    shoulder_symmetry_ok and elbow_symmetry_ok)
        
        result = {
            'is_t_pose': is_t_pose,
            'reason': '',
            'angles': {
                'left_shoulder': left_shoulder_angle,
                'right_shoulder': right_shoulder_angle,
                'left_elbow': left_elbow_angle,
                'right_elbow': right_elbow_angle
            },
            'status': {
                'left_shoulder': is_left_shoulder_ok,
                'right_shoulder': is_right_shoulder_ok,
                'left_elbow': is_left_elbow_ok,
                'right_elbow': is_right_elbow_ok,
                'shoulder_symmetry': shoulder_symmetry_ok,
                'elbow_symmetry': elbow_symmetry_ok
            }
        }
        
        if not is_t_pose:
            failed = []
            if not is_left_shoulder_ok:
                failed.append("левое плечо")
            if not is_right_shoulder_ok:
                failed.append("правое плечо")
            if not is_left_elbow_ok:
                failed.append("левый локоть")
            if not is_right_elbow_ok:
                failed.append("правый локоть")
            if not shoulder_symmetry_ok:
                failed.append("симметрия плеч")
            if not elbow_symmetry_ok:
                failed.append("симметрия локтей")
                
            result['reason'] = f"Не выполнено: {', '.join(failed)}"
        
        return result
        
    def setup_mqtt_callbacks(self):
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.mqtt_connected = True
            client.subscribe(self.mqtt_topic)
            self.mqtt_subscribed = True
            print(f" Успешное подключение к MQTT брокеру: {self.mqtt_broker}")
            print(f" Подписан на топик: {self.mqtt_topic}")
        else:
            print(f"Ошибка подключения к MQTT брокеру. Код: {rc}")
            self.mqtt_connected = False
            
    def _on_mqtt_message(self, client, userdata, msg):
        try:
            self.mqtt_data_received = True
            self.mqtt_last_message_time = time.time()
            
            data = msg.payload.decode().strip()
            
            if ' ' in data:
                numbers = list(map(float, data.split()))
            else:
                return
                
            if len(numbers) >= NUM_POINTS * NUM_COORDINATES:
                for i in range(NUM_POINTS):
                    idx = i * NUM_COORDINATES
                    x = numbers[idx]
                    y = numbers[idx + 1]
                    z = numbers[idx + 2]
                    self.points[i] = (x, y, z)
                
                self.calculate_all_angles()
                    
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def calculate_angle(self, p1_idx, p2_idx, p3_idx):
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
        p1 = self.points[p1_idx]
        p2 = self.points[p2_idx]
        p3 = self.points[p3_idx]
        
        v1 = (p1[0] - p2[0], p1[1] - p2[1])  
        v2 = (p3[0] - p2[0], p3[1] - p2[1]) 
        
        angle1 = math.atan2(v1[1], v1[0])
        angle2 = math.atan2(v2[1], v2[0])
        

        angle_diff = abs(angle1 - angle2)
        
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        
        return math.degrees(angle_diff)
    
    def calculate_all_angles(self):
        """Вычисляет все углы между связанными точками"""
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
    
    def get_specific_angles(self):
        """Получает конкретные важные углы тела"""
        specific_angles = {}
        
        # Плечи (угол между рукой и туловищем)
        left_shoulder = self.calculate_angle(13, 11, 23)
        right_shoulder = self.calculate_angle(14, 12, 24)
        
        # Локти (угол в локтевом суставе)
        left_elbow = self.calculate_angle(11, 13, 15)
        right_elbow = self.calculate_angle(12, 14, 16)
        
        # Тазобедренные суставы (угол между бедром и туловищем)
        left_hip = self.calculate_angle(25, 23, 11)
        right_hip = self.calculate_angle(26, 24, 12)
        
        # Колени (угол в коленном суставе)
        left_knee = self.calculate_angle(23, 25, 27)
        right_knee = self.calculate_angle(24, 26, 28)
        
        specific_angles['left_elbow'] = {
            'angle': left_elbow,
            'points': (11, 13, 15),
            'name': 'Левый локоть'
        }
        
        specific_angles['right_elbow'] = {
            'angle': right_elbow,
            'points': (12, 14, 16),
            'name': 'Правый локоть'
        }
        
        specific_angles['left_shoulder'] = {
            'angle': left_shoulder,
            'points': (13, 11, 23),
            'name': 'Левое плечо'
        }
        
        specific_angles['right_shoulder'] = {
            'angle': right_shoulder,
            'points': (14, 12, 24),
            'name': 'Правое плечо'
        }
        
        specific_angles['left_knee'] = {
            'angle': left_knee,
            'points': (23, 25, 27),
            'name': 'Левое колено'
        }
        
        specific_angles['right_knee'] = {
            'angle': right_knee,
            'points': (24, 26, 28),
            'name': 'Правое колено'
        }
        
        specific_angles['left_hip'] = {
            'angle': left_hip,
            'points': (25, 23, 11),
            'name': 'Левый тазобедренный'
        }
        
        specific_angles['right_hip'] = {
            'angle': right_hip,
            'points': (26, 24, 12),
            'name': 'Правый тазобедренный'
        }
        
        return specific_angles
    
    def print_specific_angles(self):
        """Выводит конкретные важные углы"""
        specific_angles = self.get_specific_angles()
        
        if not specific_angles:
            print("Нет данных об углах")
            return
    
    def check_mqtt_connection(self):
        if not self.mqtt_client:
            return False, False, False
        
        connected = self.mqtt_connected
        subscribed = self.mqtt_subscribed
        
        data_recent = False
        if self.mqtt_data_received and (time.time() - self.mqtt_last_message_time) < 5:
            data_recent = True
        
        return connected, subscribed, data_recent
    
    def connect(self, timeout=5):
        try:
            print(f"Попытка подключения к MQTT брокеру {self.mqtt_broker}:{self.mqtt_port}...")
            print(f"Топик для подписки: {self.mqtt_topic}")
            
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            print(f"Ожидание подключения... (до {timeout} секунд)")
            start_time = time.time()
            while not self.mqtt_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.mqtt_connected:
                print("Не удалось подключиться к MQTT брокеру в течение заданного времени")
                return False
            
            print("Ожидание данных...")
            start_time = time.time()
            while not self.mqtt_data_received and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            connected, subscribed, data_received = self.check_mqtt_connection()
            
            if not connected:
                print("Соединение с MQTT брокером не установлено")
                return False
            elif not subscribed:
                print("Не удалось подписаться на топик")
                return False
            elif not data_received:
                print(f"Предупреждение: Нет данных из топика '{self.mqtt_topic}'")
                print("Проверьте:")
                print(f"  1. Существует ли топик '{self.mqtt_topic}' на брокере")
                print(f"  2. Отправляются ли данные в этот топик")
                return False
            else:
                print("MQTT подключение активно, данные поступают")
                return True
                
        except Exception as e:
            print(f"Ошибка подключения к MQTT: {e}")
            return False
    
    def disconnect(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("Отключено от MQTT брокера")
    
    def get_point(self, index):
        if 0 <= index < NUM_POINTS:
            return self.points[index]
        return None
    
    def get_all_points(self):
        return self.points.copy()
    
    def load_test_points(self):
        """Загружает тестовые данные для проверки работы анализатора"""
        print("Загрузка тестовых данных...")
        for i in range(min(len(TEST_POINTS), NUM_POINTS)):
            self.points[i] = tuple(TEST_POINTS[i])
        print(f"Загружено {len(TEST_POINTS)} тестовых точек")
        self.calculate_all_angles()
        return True

def test_analyzer_with_data():
    """Тестирование анализатора с предоставленными данными"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ АНАЛИЗАТОРА УГЛОВ (XY проекция)")
    print("="*60)
    
    analyzer = AngleAnalyzer()
    
    analyzer.load_test_points()
    
    print("\n=== РЕЗУЛЬТАТЫ (XY ПРОЕКЦИЯ) ===")
    analyzer.calculate_all_angles()
    analyzer.print_specific_angles()
    
    specific_angles = analyzer.get_specific_angles()
    
    print("\n" + "="*60)
    print("ИНДИВИДУАЛЬНЫЕ ЗНАЧЕНИЯ:")
    print("="*60)
    for key in ['right_elbow', 'left_elbow', 'right_shoulder', 'left_shoulder', 'right_knee', 'left_knee']:
        if key in specific_angles:
            angle_data = specific_angles[key]
            print(f"{angle_data['name']:25}: {angle_data['angle']:6.1f}°")
    
    print("\nТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)

if __name__ == "__main__":
    print("Выберите режим работы:")
    print("1. Тестирование с предоставленными данными")
    print("2. Работа через MQTT (реальный режим)")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "1":
        analyzer = AngleAnalyzer() 
        analyzer.load_test_points()
        analyzer.calculate_all_angles()
        specific_angles = analyzer.get_specific_angles()
        print("\nИНДИВИДУАЛЬНЫЕ ЗНАЧЕНИЯ:")
        print("="*60)
        for key in ['right_elbow', 'left_elbow', 'right_shoulder', 'left_shoulder', 'right_knee', 'left_knee']:
            if key in specific_angles:
                angle_data = specific_angles[key]
                print(f"{angle_data['name']:25}: {angle_data['angle']:6.1f}°")
        
        t_pose_result = analyzer.check_t_pose()
        print("\n=== ПРОВЕРКА T-ПОЗЫ ===")
        print(f"T-поза: {'ВЕРНО' if t_pose_result['is_t_pose'] else 'НЕВЕРНО'}")
        print(f"Причина: {t_pose_result['reason']}")
        print(f"Углы: Л-плечо={t_pose_result['angles']['left_shoulder']:.1f}°, "
              f"П-плечо={t_pose_result['angles']['right_shoulder']:.1f}°, "
              f"Л-локоть={t_pose_result['angles']['left_elbow']:.1f}°, "
              f"П-локоть={t_pose_result['angles']['right_elbow']:.1f}°")
        
        print("\nТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        
    else:
        analyzer = AngleAnalyzer(
            broker=MQTT_BROKER,
            port=MQTT_PORT,
            topic=MQTT_TOPIC
        )
        
        if analyzer.connect(timeout=5):
            print("Анализатор успешно подключен и готов к работе")
            print("Используется XY проекция для вычисления углов")
            
            try:
                update_counter = 0
                while True:
                    if update_counter % 10 == 0:
                        analyzer.print_specific_angles()
                        
                        
                    specific_angles = analyzer.get_specific_angles()
                    t_pose_result = analyzer.check_t_pose()
                    print(f"T-поза: {'ВЕРНО' if t_pose_result['is_t_pose'] else 'НЕВЕРНО'}")
                    print(f"Причина: {t_pose_result['reason']}")
                    print(f"Углы: Л-плечо={t_pose_result['angles']['left_shoulder']:.1f}°, "
                          f"П-плечо={t_pose_result['angles']['right_shoulder']:.1f}°, "
                          f"Л-локоть={t_pose_result['angles']['left_elbow']:.1f}°, "
                          f"П-локоть={t_pose_result['angles']['right_elbow']:.1f}°")
                    if update_counter % 5 == 0 and specific_angles:
                        print(f"\nОбновление #{update_counter}")
                        print(f"Правый локоть: {specific_angles['right_elbow']['angle']:.1f}°")
                        print(f"Левый локоть: {specific_angles['left_elbow']['angle']:.1f}°")
                        print(f"Правое плечо: {specific_angles['right_shoulder']['angle']:.1f}°")
                        print(f"Левое плечо: {specific_angles['left_shoulder']['angle']:.1f}°")
                    
                    update_counter += 1
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nЗавершение работы...")
                analyzer.disconnect()
        else:
            print("Не удалось подключиться к MQTT брокеру или получить данные")
            print("Завершение работы...")
