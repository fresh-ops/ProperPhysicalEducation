import os
import paho.mqtt.client as mqtt
import struct 
import time
import json
from emg_filter import EMGFilter


MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-broker')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
EMG_DATA_TOPIC = "emg/raw"
EMG_FILTERED_DATA_TOPIC = "emg/filtered"
CAMERA_POINTS_TOPIC = "camera/points"


def on_connect(client, userdata, flags, reason_code):
    if reason_code == 0:
        print(f"Connected with result code {reason_code}")
        client.subscribe(EMG_DATA_TOPIC)
        client.subscribe(CAMERA_POINTS_TOPIC)
    else:
        print(f"Failed to connect, return code {reason_code}")


def on_message(client, userdata, message):
    match message.topic:
        case "emg/raw":
            try:
                if len(message.payload) != 2:
                    return

                value_tuple = struct.unpack('<H', message.payload)
                raw_value = float(value_tuple[0])
                filtered_value = filter.filter(raw_value)
            
                client.publish(EMG_FILTERED_DATA_TOPIC, str(filtered_value))

            except Exception as e:
                print(f"EMG_DATA_TOPIC error: {e}")
        case "emg/points":
            try:
                points = json.loads(message.payload.decode('utf-8'))
                print(points)
            except Exception as e:
                print(f"CAMERA_POINTS_TOPIC error: {e}")



# Инициализация MQTT клиента
client = mqtt.Client()
filter = EMGFilter()
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
client.loop_start()
