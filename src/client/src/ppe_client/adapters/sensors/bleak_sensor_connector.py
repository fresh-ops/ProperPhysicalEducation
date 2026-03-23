import asyncio

from bleak import BleakClient

from ppe_client.application.sensors.ports import SensorConnector
from ppe_client.domain import SensorDescriptor


class BleakSensorConnector(SensorConnector):
    DEVICE_UUID = "0000503e-0000-1000-8000-00805f9b34fb"

    def __init__(self) -> None:
        self._clients: dict[str, BleakClient] = {}
        self._lock = asyncio.Lock()

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        async with self._lock:
            if descriptor.identity in self._clients:
                return self._clients[descriptor.identity].is_connected

            try:
                client = BleakClient(descriptor.address)
                await client.connect()
                if client.is_connected:
                    self._clients[descriptor.identity] = client
                    return True
                return False
            except Exception:
                return False

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        async with self._lock:
            client = self._clients.pop(descriptor.identity, None)
            if client and client.is_connected:
                await client.disconnect()

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        client = self._clients.get(descriptor.identity)
        return client is not None and client.is_connected

    async def cleanup(self) -> None:
        async with self._lock:
            for client in self._clients.values():
                if client.is_connected:
                    await client.disconnect()
            self._clients.clear()