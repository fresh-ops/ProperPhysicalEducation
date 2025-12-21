import os
import paho.mqtt.client as mqtt
import numpy as np
import struct 
import time
import random

# Чтение переменных окружения для конфигурации
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-broker')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

# Константы для фильтрации
last = 0.0
Data = 0.0
lastD = 0.0
fk = 0.3

# Пример функции для генерации данных позы
def detect_pose():
    pose = {
        "pose_id": random.choice([-1,0,1]),
        "angles": [random.uniform(60,120) for _ in range(6)],
        "deviations": [random.uniform(0,15) for _ in range(6)],
        "log": {
            "is_correct": random.choice([True, False]),
            "needed_correction": [random.uniform(-10,10) for _ in range(6)]
        }
    }
    return pose


# Экспоненциальное скользящее среднее (фильтр)
def filter_ema(raw_value):
    global last, Data, lastD, fk
    lastD = Data
    Data = abs(last - raw_value) * fk + Data * (1.0 - fk)
    last = raw_value
    return Data

# Подключение к MQTT брокеру по топикам
def on_connect(client, userdata, flags, rc):
    """Вызывается при установлении соединения с брокером."""
    if rc == 0:
        print("Connected with result code " + str(rc))
        client.subscribe("emg/raw")
        client.subscribe("camera/points")
    else:
        print("Failed to connect, return code " + str(rc))

# Обработка входящих сообщений
def on_message(client, userdata, msg):
    #emg
    if msg.topic == "emg/raw":
        try:
            print(f"[RECV] topic={msg.topic} payload={msg.payload}")

            if len(msg.payload) != 2:
                return

            value_tuple = struct.unpack('<H', msg.payload)
            raw_value = float(value_tuple[0])
            filtered_value = filter_ema(raw_value)
            
            client.publish("emg/filtered", str(filtered_value))
            print(f"[EMG] raw={raw_value} filtered={filtered_value}")

        except Exception as e:
            print("EMG Error:", e)


# Инициализация MQTT клиента
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Попытки подключения с повторными попытками
max_retries = 10
retry_delay = 2

for attempt in range(max_retries):
    try:
        print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} (attempt {attempt + 1}/{max_retries})")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print(f"Connection failed: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries reached. Exiting.")
            exit(1)

print("Connected successfully! Starting loop...")
client.loop_forever()