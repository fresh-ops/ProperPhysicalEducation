#pragma once

#include <Arduino.h>
#include <BLEConfig.h>
#include <functional>

class BLEServer;
class BLEAdvertising;
class BLECharacteristic;
class BLEPeripheralServerCallbacks;

using CharacteristicValueCallback = std::function<uint32_t()>;

class BLEPeripheral {
public:
  explicit BLEPeripheral(
    const char* deviceName = Config::deviceName,
    uint16_t serviceUUID = Config::serviceUUID,
    CharacteristicValueCallback callback = nullptr
  );
  void begin();
  void update();
  bool isConnected() const;

private:
  friend class BLEPeripheralServerCallbacks;

  void onConnect(BLEServer* server);
  void onDisconnect(BLEServer* server);

  const char* deviceName;
  uint16_t serviceUUID;
  CharacteristicValueCallback callback;
  BLEAdvertising* advertising = nullptr;
  BLECharacteristic* millisCharacteristic = nullptr;
  bool connected = false;
};
