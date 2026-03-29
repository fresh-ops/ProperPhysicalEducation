import asyncio
from collections.abc import Callable

from bleak import BleakClient

from ppe_client.domain import SensorDescriptor
from ppe_client.application.sensors.ports.signal_filter import SignalFilter

from .bleak_sensor_reader import BleakSensorReader
from .ema_signal_filter import EMASignalFilter 


class BleakSensorSession:
    
    def __init__(
        self, 
        client: BleakClient, 
        descriptor: SensorDescriptor,
        signal_filter: SignalFilter | None = None
    ) -> None:
        self._reader = BleakSensorReader(client)
        self._signal_filter = signal_filter or EMASignalFilter()
        self._callbacks: set[Callable[[float], None]] = set()
        self._reading_task: asyncio.Task | None = None
        self._should_stop = False

    def attach(self, callback: Callable[[float], None]) -> None:
        self._callbacks.add(callback)
        if self._reading_task is None or self._reading_task.done():
            self._start_reading()

    def detach(self, callback: Callable[[float], None]) -> None:
        self._callbacks.discard(callback)
        if not self._callbacks:
            self._stop_reading()

    def terminate(self) -> bool:
        self._stop_reading()
        return True

    def _start_reading(self) -> None:
        if self._reading_task is not None and not self._reading_task.done():
            return
        
        self._should_stop = False
        self._reading_task = asyncio.create_task(self._read_loop())

    def _stop_reading(self) -> None:
        self._should_stop = True
        if self._reading_task and not self._reading_task.done():
            self._reading_task.cancel()

    async def _read_loop(self) -> None:
        try:
            while not self._should_stop:
                try:
                    emg_value = await self._reader.read()

                    emg_value = self._signal_filter.filter(emg_value)
                    
                    for callback in self._callbacks:
                        callback(emg_value)
                    
                    await asyncio.sleep(0.01)  
                except Exception:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass