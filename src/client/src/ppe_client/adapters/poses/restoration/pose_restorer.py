from collections import deque
from collections.abc import Callable

import numpy as np
from PySide6 import QtCore

from ppe_client.application.poses.ports import PoseReciever
from ppe_client.application.poses.pose import Pose
from ppe_client.domain.camera_descriptor import CameraDescriptor, CameraIdentity

from ..pose_converter import PoseConverter
from .basis_translater import BasisTranslater


class _PoseSynchronizer(QtCore.QObject):
    SYNC_WINDOW_MS: int = 20
    MIN_RATIO: float = 0.7
    MAX_QUEUE_SIZE: int = 50

    def __init__(
        self,
        on_synchronized_callback: Callable[[list[Pose]], None],
        parent: QtCore.QObject,
    ) -> None:
        super().__init__(parent=parent)
        self._poses: dict[CameraIdentity, deque[Pose]] = {}
        self._callback = on_synchronized_callback
        self._lock = QtCore.QMutex()

    def put(self, camera_id: CameraIdentity, pose: Pose) -> None:
        self._lock.lock()
        try:
            if camera_id not in self._poses:
                self._poses[camera_id] = deque()

            queue = self._poses[camera_id]
            queue.append(pose)

            if len(queue) > self.MAX_QUEUE_SIZE:
                queue.popleft()
        finally:
            self._lock.unlock()

        self._try_synchronize()

    def _try_synchronize(self) -> None:
        sync_window = self.SYNC_WINDOW_MS
        min_ratio = self.MIN_RATIO
        poses_dict = self._poses

        while True:
            oldest_timestamp: int | None = None
            try:
                oldest_timestamp = min(
                    (q[0].timestamp_ms for q in poses_dict.values() if q), default=None
                )
            except ValueError:
                return

            if oldest_timestamp is None:
                return

            synchronized_batch: list[Pose] = []
            cams_to_pop: list[CameraIdentity] = []

            for cam_id, queue in poses_dict.items():
                if not queue:
                    continue

                head_ts = queue[0].timestamp_ms
                if oldest_timestamp <= head_ts <= oldest_timestamp + sync_window:
                    synchronized_batch.append(queue[0])
                    cams_to_pop.append(cam_id)

            total_cameras = len(poses_dict)
            min_required = round(total_cameras * min_ratio)

            if len(synchronized_batch) < min_required:
                return

            for cam_id in cams_to_pop:
                poses_dict[cam_id].popleft()

            empty_cams = [cid for cid, q in poses_dict.items() if not q]
            for cam_id in empty_cams:
                del poses_dict[cam_id]

            self._callback(synchronized_batch)


class PoseRestorer(QtCore.QObject):
    _synchronizer: _PoseSynchronizer
    _reciever: PoseReciever | None

    def __init__(self) -> None:
        super().__init__()
        self._synchronizer = _PoseSynchronizer(self._on_synchronized, parent=self)
        self._reciever = None

    def recieve(self, pose: Pose, camera: CameraDescriptor | None = None) -> None:
        if not camera:
            return
        self._synchronizer.put(camera.identity, pose)

    def set_reciever(self, reciever: PoseReciever | None) -> PoseReciever | None:
        prev = self._reciever
        self._reciever = reciever
        return prev

    def _on_synchronized(self, poses: list[Pose]) -> None:
        if not poses or self._reciever is None:
            return

        self._reciever.recieve(self._restore(poses), None)

    def _restore(self, poses: list[Pose]) -> Pose:
        leading = self._choose_leading(poses)
        np_leading = PoseConverter.to_numpy(leading)
        np_poses = [PoseConverter.to_numpy(p) for p in poses]

        coords: list[np.ndarray] = []
        weights: list[np.ndarray] = []
        for pose in np_poses:
            coords.append(BasisTranslater.translate(np_leading[0], pose[0]))
            weights.append(pose[1])

        weights_prod = [w[:, 0] * w[:, 1] for w in weights]
        weights_stack = np.stack(weights_prod, axis=0)
        coords_stack = np.stack(coords, axis=0)

        total_weights = np.sum(weights_stack, axis=0)
        mask = total_weights > 0
        result_coords = np.zeros((33, 3), dtype=np.float32)
        if np.any(mask):
            weighted = np.sum(
                coords_stack[:, mask] * weights_stack[:, mask, np.newaxis], axis=0
            )
            result_coords[mask] = weighted / total_weights[mask, np.newaxis]
        if np.any(~mask):
            result_coords[~mask] = np.mean(coords_stack[:, ~mask], axis=0)

        visibilities = [w[:, 0] for w in weights]
        presences = [w[:, 1] for w in weights]
        mean_visibility = np.mean(np.stack(visibilities, axis=0), axis=0)
        mean_presence = np.mean(np.stack(presences, axis=0), axis=0)

        return PoseConverter.from_numpy(
            result_coords, mean_visibility, mean_presence, leading.timestamp_ms
        )

    def _choose_leading(self, poses: list[Pose]) -> Pose:
        return poses[0]
