from ppe_client.domain import CameraDescriptor


def test_identity_should_be_equal_for_same_backend_and_index() -> None:
    first = CameraDescriptor(name="Front Cam", index=0, backend=700)
    second = CameraDescriptor(name="USB Camera", index=0, backend=700)

    assert first.identity == second.identity


def test_identity_should_change_when_backend_changes() -> None:
    original = CameraDescriptor(name="Front Cam", index=0, backend=700)
    with_different_backend = CameraDescriptor(name="Front Cam", index=0, backend=1400)

    assert original.identity != with_different_backend.identity


def test_identity_should_change_when_index_changes() -> None:
    original = CameraDescriptor(name="Front Cam", index=0, backend=700)
    with_different_index = CameraDescriptor(name="Front Cam", index=1, backend=700)

    assert original.identity != with_different_index.identity


def test_identity_should_remain_stable_across_repeated_reads() -> None:
    descriptor = CameraDescriptor(name="Front Cam", index=3, backend=700)

    first = descriptor.identity
    second = descriptor.identity
    third = descriptor.identity

    assert first == second == third
