#include <Arduino.h>
#include "BLEPeripheral.h"

namespace {
uint32_t computeCharacteristicValue() {
  return millis();
}

BLEPeripheral blePeripheral(Config::deviceName, Config::serviceUUID, computeCharacteristicValue);
}

void setup() {
	blePeripheral.begin();
}

void loop() {
	blePeripheral.update();
	delay(1000);
}