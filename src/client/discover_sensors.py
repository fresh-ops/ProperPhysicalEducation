# test_mock.py
import asyncio
import os
import sys

from ppe_client.domain import SensorDescriptor

src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)


class MockBleakSensorEnumerator:
    def __init__(self, target_name: str = "PPE Sensor"):
        self._target_name = target_name

    async def discover(self, timeout_s: float = 2.0):
        print(f"Mock discovery: looking for '{self._target_name}'")
        return [
            SensorDescriptor(name="PPE Sensor", address="AA:BB:CC:DD:EE:FF"),
            SensorDescriptor(name="PPE Sensor", address="11:22:33:44:55:66"),
        ]


async def main():
    enumerator = MockBleakSensorEnumerator()
    devices = await enumerator.discover()
    print(f"\nFound {len(devices)} devices:")
    for device in devices:
        print(f"  - {device.name}: {device.address}")


if __name__ == "__main__":
    asyncio.run(main())
