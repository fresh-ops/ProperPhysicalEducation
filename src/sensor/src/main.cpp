#include <Arduino.h>

#include "ble_advertising.h"
#include "ble_config.h"
#include "ble_server.h"

static BLEState g_ble_state;

const int ANALOG_PIN = A0;

void setup() {
	Serial.begin(115200);
	pinMode(ANALOG_PIN, INPUT);
	init_ble_server(g_ble_state);
	start_ble_advertising(DEVICE_NAME, SERVICE_UUID_16);
}

void loop() {
	if (g_ble_state.device_connected && g_ble_state.timestamp_char != nullptr) {
		int rawsignal = analogRead(ANALOG_PIN);
		float voltage = rawsignal * (3.3 / 4095.0);

		g_ble_state.timestamp_char->setValue(voltage);
		g_ble_state.timestamp_char->notify();

	}
	delay(150); //you can change delay if you need
}
