#include "ble_server.h"
#include <Arduino.h>

#include <BLE2902.h>
#include <BLEDevice.h>
#include <BLEServer.h>

#include "ble_config.h"

namespace {
class ServerCallbacks : public BLEServerCallbacks {
public:
	explicit ServerCallbacks(BLEState &state) : state_(state) {}

	void onConnect(BLEServer *server) override {
		state_.device_connected = true;
	}

	void onDisconnect(BLEServer *server) override {
		state_.device_connected = false;
		server->getAdvertising()->start();
	}

private:
	BLEState &state_;
};
}

void init_ble_server(BLEState &state) {
	BLEDevice::init(DEVICE_NAME);

	BLEServer *server = BLEDevice::createServer();
	server->setCallbacks(new ServerCallbacks(state));

	BLEService *service = server->createService(BLEUUID(SERVICE_UUID_16));
	state.timestamp_char = service->createCharacteristic(
		BLEUUID(CHAR_UUID_16),
		BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
	);
	state.timestamp_char->addDescriptor(new BLE2902());
	service->start();
}
