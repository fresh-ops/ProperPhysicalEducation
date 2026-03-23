import asyncio

from ppe_client.adapters.sensors import BleakSensorEnumerator
from ppe_client.domain import SensorDescriptor


async def main() -> None:
    enumerator = BleakSensorEnumerator(target_name="PPE Sensor")
    sensors: list[SensorDescriptor] = await enumerator.discover(timeout_s=3.0)

    print(f"FOUND {len(sensors)} sensors")
    for i, s in enumerate(sensors, start=1):
        print(f"{i}. {s.name} | {s.address}")


if __name__ == "__main__":
    asyncio.run(main())