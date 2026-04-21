import os

from bleak import BleakScanner
from wireup import injectable

from ppe_client.application.sensors.ports import SensorEnumerator
from ppe_client.domain import SensorDescriptor


@injectable(as_type=SensorEnumerator)
class BleakSensorEnumerator(SensorEnumerator):
    def __init__(self, target_name: str = "PPE Sensor") -> None:
        self._target_name = target_name

    async def discover(self, timeout_s: float = 2.0) -> list[SensorDescriptor]:
        if os.getenv("PPE_TEST_MODE") == "1":
            return [
                SensorDescriptor(
                    name="PPE Sensor",
                    address="AA:BB:CC:DD:EE:FF",
                ),
                SensorDescriptor(
                    name="PPE Sensor",
                    address="11:22:33:44:55:66",
                ),
            ]

        devices = await BleakScanner.discover(timeout=timeout_s)

        result: list[SensorDescriptor] = []
        seen_addresses: set[str] = set()

        for dev in devices:
            name = getattr(dev, "name", None)
            if name is None or name != self._target_name:
                continue

            address = getattr(dev, "address", None)
            if address is None:
                continue

            if address in seen_addresses:
                continue

            seen_addresses.add(address)
            result.append(SensorDescriptor(name=name, address=address))

        return result
