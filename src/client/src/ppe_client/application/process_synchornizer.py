import asyncio
import contextlib
from asyncio import Queue
from collections import deque

from .poses import Pose
from .process_data import EmgReading, ProcessData
from .sensors import SensorValue
from ppe_client.domain import SensorDescriptor


class ProcessSynchronizer:
    _SYNC_WINDOW_MS: int = 20

    _poses: deque[Pose]
    _sensors: dict[SensorDescriptor, deque[SensorValue]]
    _poses_lock: asyncio.Lock
    _sensors_lock: asyncio.Lock
    _has_poses: asyncio.Condition
    _new_sensors: asyncio.Condition
    _queue: Queue[ProcessData]

    _task: asyncio.Task[None]

    def __init__(self) -> None:
        self._poses = deque()
        self._sensors = {}
        self._poses_lock = asyncio.Lock()
        self._sensors_lock = asyncio.Lock()
        self._has_poses = asyncio.Condition(self._poses_lock)
        self._new_sensors = asyncio.Condition(self._sensors_lock)
        self._queue = Queue()

        self._task = asyncio.create_task(self._synchronization_loop())

    async def stop(self) -> None:
        if self._task.done():
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task

    async def append_pose(self, pose: Pose) -> None:
        async with self._has_poses:
            self._poses.append(pose)
            self._has_poses.notify()

    async def append_sensor(
        self, descriptor: SensorDescriptor, value: SensorValue
    ) -> None:
        async with self._new_sensors:
            if descriptor not in self._sensors:
                self._sensors[descriptor] = deque()
            self._sensors[descriptor].append(value)
            self._new_sensors.notify()

    async def delete_sensor(self, descriptor: SensorDescriptor) -> None:
        async with self._new_sensors:
            self._sensors.pop(descriptor, None)
            self._new_sensors.notify_all()

    @property
    def queue(self) -> Queue[ProcessData]:
        return self._queue

    async def _synchronization_loop(self) -> None:
        while True:
            pose = await self._try_synchronize_pose()
            if pose is not None:
                await self._send_data(pose)

    async def _send_data(self, pose: Pose) -> None:
        emg: list[EmgReading] = []
        sync_window = self._get_sync_window(pose.timestamp_ms)
        async with self._sensors_lock:
            for descriptor, values in self._sensors.items():
                if values and values[0].timestamp_ms in sync_window:
                    value = values.popleft()
                    emg.append(EmgReading(descriptor.address, value.zone))
        await self._queue.put(ProcessData(pose, emg))

    async def _try_synchronize_pose(self) -> Pose | None:
        pose = await self._pop_pose()
        sync_window = self._get_sync_window(pose.timestamp_ms)
        async with self._new_sensors:
            while True:
                sensors_ready = 0
                after_sync_window = 0
                for values in self._sensors.values():
                    while values and values[0].timestamp_ms < sync_window.start:
                        values.popleft()

                    if not values:
                        continue
                    elif values[0].timestamp_ms in sync_window:
                        sensors_ready += 1
                    else:
                        after_sync_window += 1

                if sensors_ready == len(self._sensors):
                    return pose
                elif after_sync_window > 0:
                    return None
                await self._new_sensors.wait()

    async def _pop_pose(self) -> Pose:
        async with self._has_poses:
            await self._has_poses.wait_for(lambda: self._poses)
            return self._poses.popleft()

    def _get_sync_window(self, timestamp: int) -> range:
        return range(
            timestamp - self._SYNC_WINDOW_MS, timestamp + self._SYNC_WINDOW_MS + 1
        )
