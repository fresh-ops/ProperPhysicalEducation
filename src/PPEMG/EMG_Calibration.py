import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time
from collections import deque
import json
import os
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import messagebox

# Константы программы
EMG_SAMPLING_RATE = 1000  # Частота дискретизации ЭМГ сигнала (Гц)
MQTT_BROKER = "127.0.0.1"    # Адрес MQTT брокера
MQTT_PORT = 1883           # Порт MQTT брокера
MQTT_TOPIC = "emg/raw"     # Топик для получения данных ЭМГ
MQTT_USERNAME = None      # Имя пользователя MQTT (если требуется)
MQTT_PASSWORD = None      # Пароль MQTT (если требуется)

# Пропорции цветовых зон (зеленая/желтая/красная)
GREEN_ZONE_RATIO = 0.15   # Доля зеленой зоны (расслабление)
YELLOW_ZONE_RATIO = 0.70  # Доля желтой зоны (оптимальное напряжение)
RED_ZONE_RATIO = 0.15     # Доля красной зоны (перенапряжение)

# Параметры буфера и калибровки
BUFFER_SIZE = 500          # Размер буфера для отображения данных
CALIBRATION_DURATION = 5   # Длительность каждой фазы калибровки (секунды)
WARNING_DURATION = 5       # Длительность предупреждения перед фазой (секунды)

class EMGCalibrator:
    """
    Класс для калибровки и визуализации EMG сигнала.
    
    Осуществляет сбор данных через MQTT, калибровку на основе минимального
    и максимального значений сигнала, визуализацию в реальном времени
    с разделением на зоны (зеленая, желтая, красная) и предоставление
    обратной связи пользователю.
    """
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_TOPIC):
        """
        Инициализация калибратора EMG сигнала.
        
        Args:
            broker (str): Адрес MQTT брокера
            port (int): Порт MQTT брокера
            topic (str): Топик для подписки на данные EMG
        """
        
        self.mqtt_broker = broker
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.mqtt_client = None
        
        self.min_value = 0
        self.max_value = 0
        
        self.yellow_lower = 0
        self.yellow_upper = 0
        
        self.GREEN_ZONE_RATIO = GREEN_ZONE_RATIO
        self.YELLOW_ZONE_RATIO = YELLOW_ZONE_RATIO
        self.RED_ZONE_RATIO = RED_ZONE_RATIO
        
        self.data_buffer = deque(maxlen=BUFFER_SIZE)
        self.calibration_data = {'relax': [], 'tense': []}
        
        self.is_calibrating = False
        self.calibration_phase = None  # 'warning_relax', 'relax', 'warning_tense', 'tense'
        self.calibration_timer = 0
        self.calibration_duration = CALIBRATION_DURATION
        self.warning_duration = WARNING_DURATION
        
        self.current_value = 0
        self.current_zone = "UNKNOWN"
        self.prev_zone = None
        
        self.running = True
        self.last_update_time = 0
        
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.3)
        
        self.create_buttons()
        
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        
        self.yellow_lower_line = self.ax.axhline(y=0, color='green', linestyle='--', alpha=0.5)
        self.yellow_upper_line = self.ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        self.green_fill = None
        self.yellow_fill = None
        self.red_fill = None
        
        self.status_text = self.ax.text(0.98, 0.95, 'Статус: Ожидание калибровки', 
                                        transform=self.ax.transAxes, fontsize=12, 
                                        verticalalignment='top', horizontalalignment='right',
                                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        self.zone_text = self.ax.text(0.3, 1.1 , 'ЗОНА: ---', 
                                      transform=self.ax.transAxes, fontsize=20, fontweight='bold',
                                      verticalalignment='top', horizontalalignment='right',
                                      bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.9, linewidth=2))
        
        self.feedback_text = self.ax.text(1.1, 1.1, '---', 
                                          transform=self.ax.transAxes, fontsize=18, 
                                          verticalalignment='top', horizontalalignment='right',
                                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, linewidth=2))
        
        self.legend_text = self.ax.text(0.98, 0.02, 
                                        'ЗЕЛЁНАЯ ЗОНА: расслабление\n' +
                                        'ЖЁЛТАЯ ЗОНА: оптимально\n' +
                                        'КРАСНАЯ ЗОНА: перенапряжение', 
                                        transform=self.ax.transAxes, fontsize=10,
                                        verticalalignment='bottom', horizontalalignment='right',
                                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        self.ax.set_xlim(0, BUFFER_SIZE)
        self.ax.set_ylim(0, 1000)
        self.ax.set_xlabel('Время (отсчёты)', fontsize=12)
        self.ax.set_ylabel('ЭМГ сигнал (мкВ)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        self.zone_colors = {
            "GREEN": "lightgreen",
            "YELLOW": "lightyellow",
            "RED": "lightcoral"
        }
        
        self.zone_names = {
            "GREEN": "ЗЕЛЁНАЯ",
            "YELLOW": "ЖЁЛТАЯ", 
            "RED": "КРАСНАЯ"
        }
        
    def create_buttons(self):
        """Создает кнопки управления в интерфейсе по заданным координатам и размерам."""
        ax_calibrate = plt.axes([0.04, 0.15, 0.3, 0.075])
        self.btn_calibrate = Button(ax_calibrate, 'Начать калибровку', color='lightblue', hovercolor='blue')
        self.btn_calibrate.on_clicked(self.start_calibration)
        
        ax_load_calib = plt.axes([0.36, 0.15, 0.3, 0.075])
        self.btn_load_calib = Button(ax_load_calib, 'Загрузить калибровку', color='lightgreen', hovercolor='green')
        self.btn_load_calib.on_clicked(lambda event: self.load_calibration())

        ax_reset = plt.axes([0.68, 0.15, 0.25, 0.075])
        self.btn_reset = Button(ax_reset, 'Сброс калибровки', color='lightcoral', hovercolor='red')
        self.btn_reset.on_clicked(self.reset_calibration)

        self.calib_indicator = plt.axes([0.405, 0.05, 0.8, 0.04], facecolor='lightgray')
        self.calib_progress = self.calib_indicator.barh(0, 0, height=0.9, color='blue')
        self.calib_indicator.set_xlim(0, 2 * (self.calibration_duration + self.warning_duration))
        self.calib_indicator.set_ylim(0, 1)
        self.calib_indicator.axis('off')
        
        self.calib_text_area = plt.axes([0.1, 0.07, 0.8, 0.05], facecolor='none')
        self.calib_text_area.axis('off')
        self.calib_text = self.calib_text_area.text(0.51, 0.5, 'ГОТОВ К КАЛИБРОВКЕ', 
                                                    ha='center', va='center', fontsize=14, fontweight='bold',
                                                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def ask_use_last_calibration(self):
        """
        Спрашивает пользователя, использовать ли последнюю калибровку.
        
        Returns:
            bool: True, если пользователь хочет использовать предыдущую калибровку,
                  False в противном случае
        """
        root = tk.Tk()
        root.withdraw()  
        
        calibration_exists = os.path.exists('emg_calibration.json')
        
        if not calibration_exists:
            return False
        
        try:
            with open('emg_calibration.json', 'r') as f:
                calibration = json.load(f)
            
            timestamp = time.ctime(calibration['timestamp'])
            min_val = calibration['min_value']
            max_val = calibration['max_value']
            
            message = f"Обнаружена предыдущая калибровка:\n" \
                     f"Дата: {timestamp}\n" \
                     f"Мин. значение: {min_val:.0f} мкВ\n" \
                     f"Макс. значение: {max_val:.0f} мкВ\n\n" \
                     f"Использовать эту калибровку?"
            
            result = messagebox.askyesno("Использовать предыдущую калибровку?", message)
            return result
            
        except Exception as e:
            print(f"Ошибка чтения калибровки: {e}")
            return False
    
    def on_mqtt_message(self, client, userdata, message):
        """
        Обработчик входящих сообщений MQTT.
        
        Args:
            client: Клиент MQTT
            userdata: Пользовательские данные
            message: Сообщение MQTT
        """
        try:
            payload = message.payload.decode('utf-8').strip()
            
            if ':' in payload:
                value = float(payload.split(':')[1].strip())
            else:
                value = float(payload)
            
            self.current_value = value
            self.data_buffer.append(value)
            
        except Exception as e:
            print(f"Ошибка обработки MQTT сообщения: {e}")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """
        Callback-функция при подключении к MQTT брокеру.
        
        Args:
            client: Клиент MQTT
            userdata: Пользовательские данные
            flags: Флаги подключения
            rc: Код результата подключения
        """
        
        if rc == 0:
            print(f"Успешное подключение к MQTT брокеру: {self.mqtt_broker}")
            client.subscribe(self.mqtt_topic)
            print(f"Подписан на топик: {self.mqtt_topic}")
        else:
            print(f"Ошибка подключения к MQTT брокеру. Код: {rc}")
    
    def connect_mqtt(self):
        """
        Подключение к MQTT брокеру.
        
        Returns:
            bool: True, если подключение успешно, False в противном случае
        """
        
        try:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            
            if MQTT_USERNAME and MQTT_PASSWORD:
                self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к MQTT: {e}")
            return False
    
    def determine_zone(self, value):
        """
        Определяет цветовую зону для текущего значения сигнала.
        
        Args:
            value (float): Текущее значение EMG сигнала
            
        Returns:
            str: Идентификатор зоны ("GREEN", "YELLOW", "RED")
        """
        
        if self.min_value == 0 and self.max_value == 0:
            return "UNKNOWN"
        
        if value < self.yellow_lower:
            return "GREEN"
        elif value <= self.yellow_upper:
            return "YELLOW"
        else:
            return "RED"
    
    def get_feedback_message(self, zone):
        """
        Формирует сообщение обратной связи в зависимости от зоны.
        Теперь показывает рекомендацию ПОСТОЯННО, пока пользователь в зоне.
        
        Args:
            zone (str): Текущая зона
            
        Returns:
            str: Сообщение обратной связи
        """
        
        if zone == "UNKNOWN":
            return "ТРЕБУЕТСЯ КАЛИБРОВКА"
        
        messages = {
            "GREEN": "НАПРЯГИСЬ!",
            "YELLOW": "МОЛОДЕЦ. ДЕРЖИ ТАК",
            "RED": "РАССЛАБЬСЯ!"
        }
        
        return messages.get(zone, "---")
    
    def update_display(self, zone, feedback):
        """
        Обновляет текстовые элементы отображения.
        
        Args:
            zone (str): Текущая цветовая зона
            feedback (str): Сообщение обратной связи
        """
        
        if self.min_value == 0 and self.max_value == 0:
            self.zone_text.set_text('ЗОНА: ---')
            self.zone_text.set_bbox(dict(boxstyle='round', facecolor='lightgray', alpha=0.9, linewidth=2))
            self.feedback_text.set_text('ТРЕБУЕТСЯ КАЛИБРОВКА')
            self.feedback_text.set_color('black')
            self.feedback_text.set_fontweight('normal')
            return
        
        if zone == "UNKNOWN":
            self.zone_text.set_text('ЗОНА: ---')
            self.zone_text.set_bbox(dict(boxstyle='round', facecolor='lightgray', alpha=0.9, linewidth=2))
            self.feedback_text.set_text('ТРЕБУЕТСЯ КАЛИБРОВКА')
            self.feedback_text.set_color('black')
            self.feedback_text.set_fontweight('normal')
            return
        
        zone_name = self.zone_names.get(zone, "---")
        self.zone_text.set_text(f'ЗОНА: {zone_name}')
        self.zone_text.set_bbox(dict(boxstyle='round', 
                                    facecolor=self.zone_colors.get(zone, 'lightgray'), 
                                    alpha=0.9,
                                    linewidth=2))
        
        self.feedback_text.set_text(f'{feedback}')
        
        if zone == "GREEN":
            self.feedback_text.set_color('darkgreen')
            self.feedback_text.set_fontweight('bold')
        elif zone == "YELLOW":
            self.feedback_text.set_color('darkorange')
            self.feedback_text.set_fontweight('bold')
        elif zone == "RED":
            self.feedback_text.set_color('darkred')
            self.feedback_text.set_fontweight('bold')
        else:
            self.feedback_text.set_color('black')
            self.feedback_text.set_fontweight('normal')
    
    def update_zones(self):
        """Обновляет границы цветовых зон на основе калибровочных значений."""
        total_range = self.max_value - self.min_value
        
        self.yellow_lower = self.min_value + total_range * self.GREEN_ZONE_RATIO
        self.yellow_upper = self.yellow_lower + total_range * self.YELLOW_ZONE_RATIO
        
        self.yellow_lower_line.set_ydata([self.yellow_lower, self.yellow_lower])
        self.yellow_upper_line.set_ydata([self.yellow_upper, self.yellow_upper])
        
        if self.green_fill:
            self.green_fill.remove()
        if self.yellow_fill:
            self.yellow_fill.remove()
        if self.red_fill:
            self.red_fill.remove()
        
        x_limits = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        
        self.green_fill = self.ax.fill_between(x_limits, 
                                              y_min, 
                                              self.yellow_lower, 
                                              color='lightgreen', alpha=0.3)
        
        self.yellow_fill = self.ax.fill_between(x_limits, 
                                               self.yellow_lower, 
                                               self.yellow_upper, 
                                               color='lightyellow', alpha=0.3)
        
        self.red_fill = self.ax.fill_between(x_limits, 
                                            self.yellow_upper, 
                                            y_max,  
                                            color='lightcoral', alpha=0.3)
    
    def start_calibration(self, event):
        """
        Начинает процесс калибровки.
        
        Args:
            event: Событие нажатия кнопки
        """
                
        if self.is_calibrating:
            return
        if self.min_value != 0 or self.max_value != 0:
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno("Начать новую калибровку?", 
                                        "Текущая калибровка будет потеряна.\nПродолжить?")
            if not result:
                return
        
        self.is_calibrating = True
        self.calibration_phase = 'warning_relax' 
        self.calibration_timer = 0
        self.calibration_data = {'relax': [], 'tense': []}
        
        print("Начинаем калибровку...")
        print(f"1. Подготовка к расслаблению ({self.warning_duration} секунд)...")
        self.calib_text.set_text(f'ГОТОВЬТЕСЬ РАССЛАБИТЬ РУКУ...')
        self.calib_text.set_bbox(dict(boxstyle='round', facecolor='orange', alpha=0.9))
        self.calib_progress[0].set_color('orange')
    
    def update_calibration(self):
        """Обновляет процесс калибровки (вызывается периодически)."""
        if not self.is_calibrating:
            return
        
        self.calibration_timer += 0.05 
        
        progress = self.calibration_timer
        self.calib_progress[0].set_width(progress)
        
        if self.calibration_phase == 'warning_relax':
            if self.calibration_timer >= self.warning_duration:
                self.calibration_phase = 'relax'
                self.calibration_timer = 0
                print("2. РАССЛАБЬТЕ руку полностью (5 секунд)")
                self.calib_text.set_text('РАССЛАБЬТЕ РУКУ...')
                self.calib_text.set_bbox(dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
                self.calib_progress[0].set_color('blue')
        
        elif self.calibration_phase == 'relax':
            self.calibration_data['relax'].append(self.current_value)
            
            if self.calibration_timer >= self.calibration_duration:
                self.calibration_phase = 'warning_tense'
                self.calibration_timer = 0
                print(f"3. Подготовка к напряжению ({self.warning_duration} секунд)...")
                self.calib_text.set_text(f'ГОТОВЬТЕСЬ НАПРЯЧЬ РУКУ...')
                self.calib_text.set_bbox(dict(boxstyle='round', facecolor='orange', alpha=0.9))
                self.calib_progress[0].set_color('orange')
        
        elif self.calibration_phase == 'warning_tense':
            if self.calibration_timer >= self.warning_duration:
                self.calibration_phase = 'tense'
                self.calibration_timer = 0
                print("4. НАПРЯГИТЕ руку максимально (5 секунд)")
                self.calib_text.set_text('НАПРЯГИТЕ РУКУ!')
                self.calib_text.set_bbox(dict(boxstyle='round', facecolor='lightcoral', alpha=0.9))
                self.calib_progress[0].set_color('red')
        
        elif self.calibration_phase == 'tense':
            self.calibration_data['tense'].append(self.current_value)
            
            if self.calibration_timer >= self.calibration_duration:
                self.finish_calibration()
    
    def finish_calibration(self):
        """Завершает процесс калибровки и сохраняет результаты."""
        self.is_calibrating = False
        
        if len(self.calibration_data['relax']) > 10 and len(self.calibration_data['tense']) > 10:
            self.min_value = np.median(self.calibration_data['relax'])
            self.max_value = np.median(self.calibration_data['tense'])
            
            self.min_value = max(0, self.min_value * 0.9)
            self.max_value = self.max_value * 1.1
            
            print(f"Калибровка завершена:")
            print(f"  Мин. (расслабление): {self.min_value:.1f} мкВ")
            print(f"  Макс. (напряжение): {self.max_value:.1f} мкВ")
            print(f"  Диапазон: {self.max_value - self.min_value:.1f} мкВ")
            
            self.update_zones()
            
            self.save_calibration()
            
            self.status_text.set_text(f'Статус: Калибровано ({self.min_value:.0f}-{self.max_value:.0f} мкВ)')
            self.calib_text.set_text('КАЛИБРОВКА ЗАВЕРШЕНА!')
            self.calib_text.set_bbox(dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))
            self.calib_progress[0].set_color('green')
            
            buffer = (self.max_value - self.min_value) * 0.2
            self.ax.set_ylim(max(0, self.min_value - buffer), self.max_value + buffer)
        else:
            print("Ошибка калибровки: недостаточно данных")
            self.status_text.set_text('Статус: Ошибка калибровки')
            self.calib_text.set_text('ОШИБКА! ПОПРОБУЙТЕ СНОВА')
            self.calib_text.set_bbox(dict(boxstyle='round', facecolor='red', alpha=0.9))
            self.calib_progress[0].set_color('red')
    
    def save_calibration(self, filename='emg_calibration.json'):
        """
        Сохраняет параметры калибровки в JSON файл.
        
        Args:
            filename (str): Имя файла для сохранения
        """
        
        calibration = {
            'min_value': float(self.min_value),
            'max_value': float(self.max_value),
            'yellow_lower': float(self.yellow_lower),
            'yellow_upper': float(self.yellow_upper),
            'timestamp': time.time()
        }
        
        with open(filename, 'w') as f:
            json.dump(calibration, f, indent=2)
        
        print(f"Калибровка сохранена в {filename}")
    
    def load_calibration(self, event=None, filename='emg_calibration.json'):
        """
        Загружает параметры калибровки из JSON файлa.
        
        Args:
            event: Событие нажатия кнопки (опционально)
            filename (str): Имя файла для загрузки
            
        Returns:
            bool: True, если загрузка успешна, False в противном случае
        """
        
        try:
            with open(filename, 'r') as f:
                calibration = json.load(f)
            
            self.min_value = calibration['min_value']
            self.max_value = calibration['max_value']
            self.yellow_lower = calibration['yellow_lower']
            self.yellow_upper = calibration['yellow_upper']
            
            self.update_zones()
            
            buffer = (self.max_value - self.min_value) * 0.2
            self.ax.set_ylim(max(0, self.min_value - buffer), self.max_value + buffer)
            
            self.status_text.set_text(f'Статус: Загружена калибровка от {time.ctime(calibration["timestamp"])}')
            print(f"Калибровка загружена из {filename}")
            
            return True
        except Exception as e:
            print(f"Ошибка загрузки калибровки: {e}")
            return False
    
    def reset_calibration(self, event):
        """
        Сбрасывает текущую калибровку.
        
        Args:
            event: Событие нажатия кнопки
        """
        
        if self.min_value == 0 and self.max_value == 0:
            return
        
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno("Сброс калибровки", 
                                    "Вы уверены, что хотите сбросить калибровку?")
        if not result:
            return
        
        self.min_value = 0
        self.max_value = 0
        self.yellow_lower = 0
        self.yellow_upper = 0
        
        self.yellow_lower_line.set_ydata([0, 0])
        self.yellow_upper_line.set_ydata([0, 0])
        
        if self.green_fill:
            self.green_fill.remove()
            self.green_fill = None
        if self.yellow_fill:
            self.yellow_fill.remove()
            self.yellow_fill = None
        if self.red_fill:
            self.red_fill.remove()
            self.red_fill = None
        
        self.zone_text.set_text('ЗОНА: ---')
        self.zone_text.set_bbox(dict(boxstyle='round', facecolor='lightgray', alpha=0.9, linewidth=2))
        
        self.feedback_text.set_text('---')
        self.feedback_text.set_color('black')
        self.feedback_text.set_fontweight('normal')
        
        self.status_text.set_text('Статус: Калибровка сброшена')
        
        self.calib_text.set_text('ГОТОВ К КАЛИБРОВКЕ')
        self.calib_text.set_bbox(dict(boxstyle='round', facecolor='white', alpha=0.8))
        self.calib_progress[0].set_color('blue')
        self.calib_progress[0].set_width(0)
        
        self.current_zone = "UNKNOWN"
        self.prev_zone = None
        
        self.ax.set_ylim(0, 1000)
    
    def update_plot(self):
        """Обновляет график данных."""
        if len(self.data_buffer) > 0:
            x_data = list(range(len(self.data_buffer)))
            self.line.set_data(x_data, list(self.data_buffer))
            
            self.ax.set_xlim(0, max(BUFFER_SIZE, len(self.data_buffer)))
    
    def run(self):
        """Запуск приложения без потоков"""
  
        use_last_calibration = self.ask_use_last_calibration()
        
        if use_last_calibration:
            print("Используется последняя калибровка")
            self.load_calibration()
        else:
            print("Будет выполнена новая калибровка")
            self.status_text.set_text('Статус: Требуется калибровка')
        
        if not self.connect_mqtt():
            print("Не удалось подключиться к MQTT брокеру. Приложение будет работать только с калибровкой.")
        
        print("Приложение запущено. Нажмите Ctrl+C для выхода.")
        
        last_update = time.time()
        try:
            while self.running:
                current_time = time.time()
                
                zone = self.determine_zone(self.current_value)
                feedback = self.get_feedback_message(zone)
                self.update_display(zone, feedback)
                
                if zone != self.current_zone:
                    print(f"Зона: {zone}, Значение: {self.current_value:.1f}")
                    self.current_zone = zone
                
                self.prev_zone = zone
                
                if self.is_calibrating:
                    self.update_calibration()
                
                if current_time - last_update > 0.05:
                    self.update_plot()
                    last_update = current_time
                
                plt.pause(0.01)
                
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
        except Exception as e:
            print(f"Ошибка в основном цикле: {e}")
        finally:
            self.close()
    
    def close(self):
        """Корректное завершение работы"""
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("Отключено от MQTT брокера")
        
        plt.close()

if __name__ == "__main__":
    calibrator = EMGCalibrator(
        broker=MQTT_BROKER, 
        port=MQTT_PORT, 
        topic=MQTT_TOPIC
    )
    
    calibrator.run()
