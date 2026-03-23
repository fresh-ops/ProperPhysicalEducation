import asyncio
import sys

from ppe_client.adapters.sensors.bleak_sensor_connector import BleakSensorConnector
from ppe_client.adapters.sensors.bleak_sensor_enumerator import BleakSensorEnumerator
from ppe_client.application.sensors.sensor_service import SensorService


async def test_sensor_connection() -> None:
    enumerator = BleakSensorEnumerator()
    connector = BleakSensorConnector()
    service = SensorService(enumerator=enumerator, connector=connector)

    print("Scanning for sensors...")
    sensors = await service.discover(timeout_s=2.0)

    if not sensors:
        print("No sensors found!")
        await service.cleanup()
        return

    print(f"Found {len(sensors)} sensor(s):")
    for sensor in sensors:
        print(f"  - {sensor.name} ({sensor.address})")

    target = sensors[0]
    print(f"\nConnecting to {target.name}...")
    connected = await service.connect(target)

    if not connected:
        print("Connection failed!")
        await service.cleanup()
        return

    print(f"Connected: {service.is_connected(target)}")
    print(f"Connected sensors: {service.get_connected_sensors()}")

    await asyncio.sleep(2.0)

    print("\nDisconnecting...")
    await service.disconnect(target)
    print(f"Connected after disconnect: {service.is_connected(target)}")

    await service.cleanup()
    print("\nCleanup complete!")


if __name__ == "__main__":
    try:
        asyncio.run(test_sensor_connection())
    except KeyboardInterrupt:
        print("\nInterrupted!")
        sys.exit(0)