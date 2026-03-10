#include "ble_utils.h"

#include <BLEDevice.h>

#include "ble_config.h"

uint16_t derive_characteristic_uuid() {
	std::string address = BLEDevice::getAddress().toString();
	uint16_t hash = 0;
	for (char c : address) {
		hash = static_cast<uint16_t>((hash * 31) + static_cast<uint8_t>(c));
	}
  
	return static_cast<uint16_t>(CHAR_UUID_BASE | (hash & 0x0FFF));
}
