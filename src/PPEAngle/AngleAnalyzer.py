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
TEST_POINTS = [[0.4446859061718, -0.04089827090502, -0.44245237112045], [0.44895234704018, -0.05287080258131, -0.42343011498451], [0.45286720991135, -0.04858280345798, -0.42341873049736], [0.45652481913567, -0.04467226937413, -0.42339262366295], [0.43799468874931, -0.05429099500179, -0.42543178796768], [0.43459764122963, -0.05047422274947, -0.42550572752953], [0.43027293682098, -0.04694251716137, -0.42560616135597], [0.45855671167374, -0.02398985438049, -0.29509773850441], [0.42317628860474, -0.0263491794467, -0.30551347136498], [0.45119950175285, -0.01137582678348, -0.39356061816216], [0.43920543789864, -0.01351650711149, -0.3967404961586], [0.50945430994034, 0.11091732978821, -0.20124647021294], [0.37641870975494, 0.12159193307161, -0.21547228097916], [0.52255845069885, 0.30523544549942, -0.11495853215456], [0.36885243654251, 0.317164093256, -0.15683460235596], [0.52618843317032, 0.46372359991074, -0.21735945343971], [0.36895373463631, 0.47633373737335, -0.24750179052353], [0.5292489528656, 0.51293474435806, -0.25318092107773], [0.36989036202431, 0.53001272678375, -0.28484842181206], [0.52042019367218, 0.51136338710785, -0.29271927475929], [0.37857621908188, 0.52475053071976, -0.32586166262627], [0.51675200462341, 0.49404391646385, -0.23399844765663], [0.38096863031387, 0.50578999519348, -0.26491197943687], [0.48194754123688, 0.44181826710701, 0.00101361738052], [0.41507160663605, 0.44614186882973, -0.00123540998902], [0.48315688967705, 0.68577617406845, 0.02980415895581], [0.41244888305664, 0.67263519763947, 0.03922303020954], [0.48580583930016, 0.88577944040299, 0.33803796768189], [0.43139961361885, 0.87547266483307, 0.32738128304482], [0.48183062672615, 0.90296614170075, 0.35970637202263], [0.43526276946068, 0.89633923768997, 0.34871357679367], [0.486258238554, 0.96423983573914, 0.21105517446995], [0.42765524983406, 0.96236550807953, 0.19612842798233]]

class AngleAnalyzer:
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC):
        self.mqtt_broker = broker
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.points = [(0.0, 0.0, 0.0)] * NUM_POINTS
        self.angles = {} 
        self.angle_history = {} 
        
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_connected = False
        self.mqtt_subscribed = False
        self.mqtt_data_received = False
        self.mqtt_last_message_time = 0
        
        self.setup_mqtt_callbacks()

    def check_arms_down_pose(self, shoulder_threshold=20, elbow_threshold=10):
        """
        Проверка позы "руки по швам"
        
        Критерии:
        - Углы в плечах: 0-20° (руки опущены вдоль тела)
        - Углы в локтях: около 180° (руки прямые)
        
        Args:
            shoulder_threshold: допустимое отклонение от 0° для плеч
            elbow_threshold: допустимое отклонение от 180° для локтей
            
        Returns:
            dict: Результаты проверки с описанием и статусом
        """
        specific_angles = self.get_specific_angles()
        
        if not specific_angles:
            return {
                'is_arms_down': False,
                'reason': 'Нет данных об углах',
                'details': {}
            }
        
        left_shoulder_angle = specific_angles['left_shoulder']['angle']
        right_shoulder_angle = specific_angles['right_shoulder']['angle']
        left_elbow_angle = specific_angles['left_elbow']['angle']
        right_elbow_angle = specific_angles['right_elbow']['angle']
        
        is_left_shoulder_ok = left_shoulder_angle <= shoulder_threshold
        is_right_shoulder_ok = right_shoulder_angle <= shoulder_threshold
        is_left_elbow_ok = abs(left_elbow_angle - 180) <= elbow_threshold
        is_right_elbow_ok = abs(right_elbow_angle - 180) <= elbow_threshold
        
        shoulder_symmetry_ok = abs(left_shoulder_angle - right_shoulder_angle) <= 15
        elbow_symmetry_ok = abs(left_elbow_angle - right_elbow_angle) <= 15
        
        is_arms_down = (is_left_shoulder_ok and is_right_shoulder_ok and
                       is_left_elbow_ok and is_right_elbow_ok and
                       shoulder_symmetry_ok and elbow_symmetry_ok)
        
        result = {
            'is_arms_down': is_arms_down,
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
        
        if not is_arms_down:
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

    def check_t_pose(self, shoulder_threshold=5, elbow_threshold=15):
        """
        Проверка Т-позы 
        
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
        """Получает конкретные важные углы тела (только для рук)"""
        specific_angles = {}
        
        # Плечи (угол между рукой и туловищем)
        left_shoulder = self.calculate_angle(13, 11, 23)
        right_shoulder = self.calculate_angle(14, 12, 24)
        
        # Локти (угол в локтевом суставе)
        left_elbow = self.calculate_angle(11, 13, 15)
        right_elbow = self.calculate_angle(12, 14, 16)

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
        
        return specific_angles
    
    def print_specific_angles(self):
        """Выводит конкретные важные углы"""
        specific_angles = self.get_specific_angles()
        
        if not specific_angles:
            print("Нет данных об углах")
            return
            
        print("\n" + "="*60)
        print("ТЕКУЩИЕ ЗНАЧЕНИЯ УГЛОВ:")
        print("="*60)
        for key in ['right_shoulder', 'left_shoulder', 'right_elbow', 'left_elbow']:
            if key in specific_angles:
                angle_data = specific_angles[key]
                print(f"{angle_data['name']:25}: {angle_data['angle']:6.1f}°")
    
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
    for key in ['right_elbow', 'left_elbow', 'right_shoulder', 'left_shoulder']:
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
        for key in ['right_elbow', 'left_elbow', 'right_shoulder', 'left_shoulder']:
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
        
        arms_down_result = analyzer.check_arms_down_pose()
        print("\n=== ПРОВЕРКА ПОЗЫ 'РУКИ ПО ШВАМ' ===")
        print(f"Руки по швам: {'ВЕРНО' if arms_down_result['is_arms_down'] else 'НЕВЕРНО'}")
        print(f"Причина: {arms_down_result['reason']}")
        print(f"Углы: Л-плечо={arms_down_result['angles']['left_shoulder']:.1f}°, "
              f"П-плечо={arms_down_result['angles']['right_shoulder']:.1f}°, "
              f"Л-локоть={arms_down_result['angles']['left_elbow']:.1f}°, "
              f"П-локоть={arms_down_result['angles']['right_elbow']:.1f}°")
        
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
                    arms_down_result = analyzer.check_arms_down_pose()
                    
                    if update_counter % 5 == 0:
                        print(f"\n=== T-ПОЗА ===")
                        print(f"T-поза: {'ДА' if t_pose_result['is_t_pose'] else 'НЕТ'}")
                        print(f"Причина: {t_pose_result['reason']}")
                        print(f"Углы: Л-плечо={t_pose_result['angles']['left_shoulder']:.1f}°, "
                              f"П-плечо={t_pose_result['angles']['right_shoulder']:.1f}°, "
                              f"Л-локоть={t_pose_result['angles']['left_elbow']:.1f}°, "
                              f"П-локоть={t_pose_result['angles']['right_elbow']:.1f}°")
                        
                        print(f"\n=== РУКИ ПО ШВАМ ===")
                        print(f"Руки по швам: {'ДА' if arms_down_result['is_arms_down'] else 'НЕТ'}")
                        print(f"Причина: {arms_down_result['reason']}")
                        print(f"Углы: Л-плечо={arms_down_result['angles']['left_shoulder']:.1f}°, "
                              f"П-плечо={arms_down_result['angles']['right_shoulder']:.1f}°, "
                              f"Л-локоть={arms_down_result['angles']['left_elbow']:.1f}°, "
                              f"П-локоть={arms_down_result['angles']['right_elbow']:.1f}°")
                    
                    update_counter += 1
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nЗавершение работы...")
                analyzer.disconnect()
        else:
            print("Не удалось подключиться к MQTT брокеру или получить данные")
            print("Завершение работы...")
