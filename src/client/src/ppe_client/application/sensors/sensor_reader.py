import asyncio
from collections.abc import Awaitable, Callable

from .ports import Sensor
from .sensor_value import SensorValue


class SensorReader:
    _sensor: Sensor
    _on_data: Callable[[SensorValue], None | Awaitable[None]]
    _on_error: Callable[[Exception], None | Awaitable[None]]
    _lock: asyncio.Lock
    _task: asyncio.Task[None] | None

    def __init__(
        self,
        sensor: Sensor,
        on_data: Callable[[SensorValue], None | Awaitable[None]],
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
                value = await self._sensor.read()
                result = self._on_data(value)
                if asyncio.iscoroutine(result):
                    await result
        except asyncio.CancelledError:
            raise
        except Exception as e:
            result = self._on_error(e)
            if asyncio.iscoroutine(result):
                await result
