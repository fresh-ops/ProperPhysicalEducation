#include <WiFi.h>
#include <PubSubClient.h>

const int ESPin = 0; // scanning port for emg signal     
const int MQTT_PORT = 1883; // port for mqtt broker
const int POLLING_RATE = 50; // refresh speed      
const unsigned long interval = 1000 / POLLING_RATE; // in milliseconds (20 ms for 50 Hz)
const char* ssid = "AndroidAP965d"; // wifi hub
const char* password = "88888888"; // password of wifi hub
const char* MQTT_MAIN_TOPIC = "emg/raw"; // topic for sending data
const char* mqtt_server = "10.120.3.71"; // IP of main device


WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastSend = 0;

// wifi connect
void setup_wifi() {
  delay(100);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

// mqtt connect
void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32_client")) {
    // success 
    } else {
      delay(2000);
    }
  }
}

// main setup
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, MQTT_PORT);
}

// 
void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();
  if (now - lastSend >= interval) {
    lastSend = now;

    int sensorValue = analogRead(ESPin);

    // 2 bytes for sending
    uint8_t payload[2];
    payload[0] = sensorValue >> 8;
    payload[1] = sensorValue & 0xFF; 

    // QoS=0
    client.publish(MQTT_MAIN_TOPIC, payload, 2, true);
  }
}