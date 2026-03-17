#pragma once

#include <BLECharacteristic.h>

struct BLEState {
	BLECharacteristic *timestamp_char = nullptr;
	bool device_connected = false;
};

void init_ble_server(BLEState &state);
