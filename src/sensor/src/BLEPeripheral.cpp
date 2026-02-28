#include "BLEPeripheral.h"

#include <BLEDevice.h>
#include <BLE2902.h>

class BLEPeripheralServerCallbacks : public BLEServerCallbacks {
public:
  explicit BLEPeripheralServerCallbacks(BLEPeripheral& blePeripheral)
      : blePeripheral(blePeripheral) {}

  void onConnect(BLEServer* server) override {
    blePeripheral.onConnect(server);
  }

  void onDisconnect(BLEServer* server) override {
    blePeripheral.onDisconnect(server);
  }

private:
  BLEPeripheral& blePeripheral;
};

BLEPeripheral::BLEPeripheral(const char* deviceName, uint16_t serviceUUID, CharacteristicValueCallback callback)
    : deviceName(deviceName), serviceUUID(serviceUUID), callback(callback) {}

void BLEPeripheral::begin() {
  BLEDevice::init(deviceName);

  BLEServer* server = BLEDevice::createServer();
  server->setCallbacks(new BLEPeripheralServerCallbacks(*this));

  BLEService* service = server->createService(BLEUUID(serviceUUID));
  
  millisCharacteristic = service->createCharacteristic(
    BLEUUID(Config::millisCharacteristicUUID),
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  millisCharacteristic->addDescriptor(new BLE2902());
  
  service->start();

  advertising = BLEDevice::getAdvertising();

  BLEAdvertisementData advertisementData;
  advertisementData.setFlags(0x06);
  advertisementData.setCompleteServices(BLEUUID(serviceUUID));

  BLEAdvertisementData scanResponseData;
  scanResponseData.setName(deviceName);

  advertising->setAdvertisementData(advertisementData);
  advertising->setScanResponseData(scanResponseData);
  advertising->start();
}

bool BLEPeripheral::isConnected() const {
  return connected;
}

void BLEPeripheral::update() {
  if (connected && millisCharacteristic != nullptr) {
    uint32_t value = callback ? callback() : millis();
    millisCharacteristic->setValue(value);
    millisCharacteristic->notify();
  }
}

void BLEPeripheral::onConnect(BLEServer* server) {
  (void)server;
  connected = true;
}

void BLEPeripheral::onDisconnect(BLEServer* server) {
  (void)server;
  connected = false;

  if (advertising != nullptr) {
    advertising->start();
  }
}
