import asyncio
import time
from collections.abc import Awaitable, Callable

from .calibration import ValueZone
from .ports import Sensor


class SensorReader:
    _sensor: Sensor
    _on_data: Callable[[float, ValueZone, float], None | Awaitable[None]]
    _on_error: Callable[[Exception], None | Awaitable[None]]
    _lock: asyncio.Lock
    _task: asyncio.Task[None] | None

    def __init__(
        self,
        sensor: Sensor,
        on_data: Callable[[float, ValueZone, float], None | Awaitable[None]],
        on_error: Callable[[Exception], None | Awaitable[None]],
    ) -> None:
        self._sensor = sensor
        self._on_data = on_data
        self._on_error = on_error
        self._lock = asyncio.Lock()
        self._task = None

    async def start(self) -> None:
        async with self._lock:
            if self._task is not None and not self._task.done():
                return

            await self._sensor.connect()
            loop = asyncio.get_running_loop()
            self._task = loop.create_task(self._loop(), name="Sensor reading task")

    async def stop(self) -> None:
        async with self._lock:
            if self._task is not None and not self._task.done():
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                finally:
                    self._task = None
                    await self._sensor.disconnect()

    async def _loop(self) -> None:
        try:
            while True:
                data, zone = await self._sensor.read_with_zone()
                timestamp_ms = time.time_ns() / 1_000_000
                result = self._on_data(data, zone, timestamp_ms)
                if asyncio.iscoroutine(result):
                    await result
        except asyncio.CancelledError:
            raise
        except Exception as e:
            result = self._on_error(e)
            if asyncio.iscoroutine(result):
                await result
