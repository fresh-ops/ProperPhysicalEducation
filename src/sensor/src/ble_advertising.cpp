#include "ble_advertising.h"

#include <BLEAdvertising.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <esp_gap_ble_api.h>

void start_ble_advertising(const char *device_name, uint16_t service_uuid_16) {
	BLEAdvertising *advertising = BLEDevice::getAdvertising();
	BLEAdvertisementData adv_data;
	BLEAdvertisementData scan_data;

	adv_data.setFlags(ESP_BLE_ADV_FLAG_GEN_DISC | ESP_BLE_ADV_FLAG_BREDR_NOT_SPT);
	adv_data.setCompleteServices(BLEUUID(service_uuid_16));
	scan_data.setName(device_name);

	advertising->setAdvertisementData(adv_data);
	advertising->setScanResponseData(scan_data);
	advertising->setAdvertisementType(ADV_TYPE_IND);
	advertising->setScanResponse(true);
	advertising->start();
}
