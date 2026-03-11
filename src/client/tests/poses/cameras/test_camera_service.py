from types import SimpleNamespace

import pytest

from src.poses.cameras.camera_service import CameraService
from src.poses.cameras.errors import CameraNotFoundError


@pytest.fixture(autouse=True)
def reset_camera_service_singleton() -> None:
    """Reset singleton state between tests to avoid cross-test pollution."""
    CameraService._instance = None


class _FakeVideoCapture:
    """Mimics cv2.VideoCapture for deterministic service tests."""

    release_calls: int = 0

    def __init__(self, index: int, backend: int | None = None) -> None:
        self._is_opened = index != 1

    def isOpened(self) -> bool:
        return self._is_opened

    def release(self) -> None:
        _FakeVideoCapture.release_calls += 1


def test_get_cameras_filters_unopenable_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    cameras = [
        SimpleNamespace(index=0, backend=200),
        SimpleNamespace(index=1, backend=200),
        SimpleNamespace(index=2, backend=200),
    ]

    monkeypatch.setattr(
        "src.poses.cameras.camera_service.enumerate_cameras",
        lambda: cameras,
    )
    monkeypatch.setattr("src.poses.cameras.camera_service.VideoCapture", _FakeVideoCapture)

    _FakeVideoCapture.release_calls = 0
    service = CameraService.get_instance()

    discovered = service.get_cameras()

    assert [camera.index for camera in discovered] == [0, 2]
    assert _FakeVideoCapture.release_calls == 3


def test_get_cameras_does_not_refresh_when_cache_populated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"count": 0}

    def fake_enumerate_cameras() -> list[SimpleNamespace]:
        calls["count"] += 1
        return [SimpleNamespace(index=0, backend=200)]

    monkeypatch.setattr(
        "src.poses.cameras.camera_service.enumerate_cameras",
        fake_enumerate_cameras,
    )
    monkeypatch.setattr("src.poses.cameras.camera_service.VideoCapture", _FakeVideoCapture)

    service = CameraService.get_instance()

    service.get_cameras()
    service.get_cameras()

    assert calls["count"] == 1


def test_get_camera_by_raises_when_index_out_of_bounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.poses.cameras.camera_service.enumerate_cameras",
        lambda: [SimpleNamespace(index=0, backend=200)],
    )
    monkeypatch.setattr("src.poses.cameras.camera_service.VideoCapture", _FakeVideoCapture)

    service = CameraService.get_instance()

    with pytest.raises(CameraNotFoundError, match="Camera with index 10 not found"):
        service.get_camera_by(10)
