import asyncio
import os

from bleak import BleakClient
from wireup import injectable

from ppe_client.application.sensors.ports import SensorConnector
from ppe_client.domain import SensorDescriptor

from .bleak_sensor_session import BleakSensorSession


@injectable
class BleakSensorConnector(SensorConnector):
    DEVICE_UUID = "0000503e-0000-1000-8000-00805f9b34fb"

    def __init__(self) -> None:
        self._clients: dict[str, BleakClient] = {}
        self._sessions: dict[str, BleakSensorSession] = {}
        self._lock = asyncio.Lock()

    async def connect(self, descriptor: SensorDescriptor) -> bool:
        async with self._lock:
            if descriptor.identity in self._clients:
                return self._clients[descriptor.identity].is_connected

            if os.getenv("PPE_TEST_MODE") == "1":
                self._sessions[descriptor.identity] = BleakSensorSession(
                    None, descriptor
                )
                return True

            try:
                client = BleakClient(descriptor.address)
                await client.connect()
                if client.is_connected:
                    self._clients[descriptor.identity] = client
                    self._sessions[descriptor.identity] = BleakSensorSession(
                        client, descriptor
                    )
                    return True
                return False
            except Exception:
                return False

    async def disconnect(self, descriptor: SensorDescriptor) -> None:
        async with self._lock:
            session = self._sessions.pop(descriptor.identity, None)
            if session:
                session.terminate()

            client = self._clients.pop(descriptor.identity, None)
            if client and client.is_connected:
                await client.disconnect()

    def is_connected(self, descriptor: SensorDescriptor) -> bool:
        return descriptor.identity in self._sessions

    def get_session(self, descriptor: SensorDescriptor) -> BleakSensorSession | None:
        return self._sessions.get(descriptor.identity)

    async def cleanup(self) -> None:
        async with self._lock:
            for session in self._sessions.values():
                session.terminate()
            self._sessions.clear()

            for client in self._clients.values():
                if client and client.is_connected:
                    await client.disconnect()
            self._clients.clear()
