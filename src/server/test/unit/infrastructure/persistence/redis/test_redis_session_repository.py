from collections.abc import AsyncIterator

import pytest
import fakeredis.aioredis
import pytest_asyncio
from infrastructure.persistence.redis.repository.redis_session_repository import (
    RedisSessionRepository,
)
from infrastructure.persistence.redis.errors import (
    RedisConnectionError,
    RedisOperationError,
)
from domain.ports.errors import EntityNotFoundError, DuplicateSessionError
from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.session import Session
from domain.model.session_id import SessionId
from redis.exceptions import ConnectionError as RedisConnectionException


@pytest_asyncio.fixture
async def fake_redis() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    redis = fakeredis.aioredis.FakeRedis()
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture
async def repo(
    fake_redis: fakeredis.aioredis.FakeRedis,
) -> RedisSessionRepository:
    return RedisSessionRepository(fake_redis, ttl=60)


@pytest.mark.asyncio
async def test_create_and_get_session(repo: RedisSessionRepository) -> None:
    session_id = SessionId("test-123")
    exercise_id = ExerciseId("ex-1")
    state = ExerciseState(current_pose_index=0, frame_tolerance_counter=0)
    session = Session(session_id, exercise_id, state)

    returned_id = await repo.create(session)
    assert returned_id == session_id

    retrieved = await repo.get(session_id)
    assert retrieved == session


@pytest.mark.asyncio
async def test_create_duplicate_fails(repo: RedisSessionRepository) -> None:
    session_id = SessionId("dup")
    session = Session(session_id, ExerciseId("ex"), ExerciseState())
    await repo.create(session)
    with pytest.raises(DuplicateSessionError, match="already exists"):
        await repo.create(session)


@pytest.mark.asyncio
async def test_update_nonexistent_fails(repo: RedisSessionRepository) -> None:
    session_id = SessionId("unknown")
    session = Session(session_id, ExerciseId("ex"), ExerciseState())
    with pytest.raises(EntityNotFoundError, match="not found"):
        await repo.update(session)


@pytest.mark.asyncio
async def test_delete(repo: RedisSessionRepository) -> None:
    session_id = SessionId("to-delete")
    session = Session(session_id, ExerciseId("ex"), ExerciseState())
    await repo.create(session)
    await repo.delete(session_id)
    with pytest.raises(EntityNotFoundError, match="not found"):
        await repo.get(session_id)


@pytest.mark.asyncio
async def test_redis_connection_error_is_wrapped(
    repo: RedisSessionRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def raise_connection_error(*args: object, **kwargs: object) -> None:
        raise RedisConnectionException("redis is unavailable")

    monkeypatch.setattr(repo._redis_client, "exists", raise_connection_error)

    session = Session(SessionId("connection-error"), ExerciseId("ex"), ExerciseState())

    with pytest.raises(RedisConnectionError, match="Error connecting to Redis"):
        await repo.create(session)


@pytest.mark.asyncio
async def test_redis_operation_error_is_wrapped(
    repo: RedisSessionRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def raise_operation_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(repo._redis_client, "delete", raise_operation_error)

    with pytest.raises(RedisOperationError, match="delete session"):
        await repo.delete(SessionId("delete-error"))
