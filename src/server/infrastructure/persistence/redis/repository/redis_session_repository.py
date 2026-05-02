from domain.model.session import Session
from domain.model.session_id import SessionId
from domain.ports.errors import EntityNotFoundError, DuplicateSessionError
from domain.ports.session_repository import SessionRepository
import redis.asyncio as redis
from redis.exceptions import ConnectionError as RedisConnectionException
from redis.exceptions import TimeoutError as RedisTimeoutException

from infrastructure.persistence.redis.errors import (
    RedisConnectionError,
    RedisOperationError,
)
from infrastructure.persistence.redis.mapper.session_mapper import SessionMapper
from infrastructure.persistence.redis.model.session import RedisSession


class RedisSessionRepository(SessionRepository):
    def __init__(self, redis_client: redis.Redis, ttl: int):
        self._redis_client = redis_client
        self._ttl = ttl

    async def create(self, session: Session) -> SessionId:
        key = self._key(session.session_id)

        exists = await self._exists(key, "create session")

        if exists:
            raise DuplicateSessionError(session.session_id.id)

        data_to_save = SessionMapper.map_to(session)
        await self._set(key, data_to_save.model_dump_json(), "create session")
        return session.session_id

    async def update(self, session: Session) -> SessionId:
        key = self._key(session.session_id)

        exists = await self._exists(key, "update session")

        if not exists:
            raise EntityNotFoundError("Session", session.session_id.id)

        data_to_update = SessionMapper.map_to(session)
        await self._set(key, data_to_update.model_dump_json(), "update session")
        return session.session_id

    async def get(self, session_id: SessionId) -> Session:
        try:
            session = await self._redis_client.get(self._key(session_id))
        except (RedisConnectionException, RedisTimeoutException) as exc:
            raise RedisConnectionError(exc) from exc
        except Exception as exc:
            raise RedisOperationError("get session", exc) from exc

        if not session:
            raise EntityNotFoundError("Session", session_id.id)

        try:
            return SessionMapper.map_from(RedisSession.model_validate_json(session))
        except Exception as exc:
            raise RedisOperationError("get session", exc) from exc

    async def delete(self, session_id: SessionId) -> None:
        try:
            await self._redis_client.delete(self._key(session_id))
        except (RedisConnectionException, RedisTimeoutException) as exc:
            raise RedisConnectionError(exc) from exc
        except Exception as exc:
            raise RedisOperationError("delete session", exc) from exc

    def _key(self, session_id: SessionId) -> str:
        return f"session:{session_id.id}"

    async def _exists(self, key: str, operation: str) -> bool:
        try:
            return bool(await self._redis_client.exists(key))
        except (RedisConnectionException, RedisTimeoutException) as exc:
            raise RedisConnectionError(exc) from exc
        except Exception as exc:
            raise RedisOperationError(operation, exc) from exc

    async def _set(self, key: str, value: str, operation: str) -> None:
        try:
            await self._redis_client.set(key, value, ex=self._ttl)
        except (RedisConnectionException, RedisTimeoutException) as exc:
            raise RedisConnectionError(exc) from exc
        except Exception as exc:
            raise RedisOperationError(operation, exc) from exc
