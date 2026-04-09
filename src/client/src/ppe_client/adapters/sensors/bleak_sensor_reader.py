import struct

from bleak import BleakClient


class BleakSensorReader:
    """Reads data from sensor via Bleak."""

    CHARACTERISTIC_UUID = "0000503f-0000-1000-8000-00805f9b34fb"

    def __init__(self, client: BleakClient) -> None:
        self._client = client

    async def read(self) -> float:
        """Read one EMG value from sensor."""
        raw_data = await self._client.read_gatt_char(self.CHARACTERISTIC_UUID)
        return float(struct.unpack("f", raw_data)[0])
