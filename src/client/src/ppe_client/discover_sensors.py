import asyncio
from ppe_client.domain import SensorDescriptor

async def main() -> None:
    print("TEST MODE: Simulating sensor discovery (timeout=3.0s)")
    
    sensors: list[SensorDescriptor] = [
        SensorDescriptor(name="PPE Sensor", address="AA:BB:CC:DD:EE:01"),
        SensorDescriptor(name="PPE Sensor", address="AA:BB:CC:DD:EE:02"),
        SensorDescriptor(name="PPE Sensor", address="AA:BB:CC:DD:EE:03"),
    ]
    
    print(f"FOUND {len(sensors)} sensors")
    for i, s in enumerate(sensors, start=1):
        print(f"{i}. {s.name} | {s.address}")

if __name__ == "__main__":
    asyncio.run(main())