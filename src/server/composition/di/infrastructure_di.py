from typing import Annotated

from wireup import Inject, injectable
import redis.asyncio as redis

from domain.ports.exercise_repository import ExerciseRepository
from domain.ports.pose_repository import PoseRepository
from domain.ports.session_repository import SessionRepository
from infrastructure.persistence.json.repository.json_exercise_repository import (
    JsonExerciseRepository,
)
from infrastructure.persistence.json.repository.json_pose_repository import (
    JsonPoseRepository,
)
from infrastructure.persistence.redis.repository.redis_session_repository import (
    RedisSessionRepository,
)


@injectable
def make_redis(
    host: Annotated[str, Inject(config="redis_host")],
    port: Annotated[int, Inject(config="redis_port")],
) -> redis.Redis:
    return redis.Redis(host=host, port=port)


@injectable
def make_session_repository(
    redis_client: redis.Redis,
    session_ttl: Annotated[int, Inject(config="session_timeout_seconds")],
) -> SessionRepository:
    return RedisSessionRepository(redis_client=redis_client, ttl=session_ttl)


@injectable
def make_exercise_repository(
    exercise_data_path: Annotated[str, Inject(config="exercise_data_path")],
) -> ExerciseRepository:
    return JsonExerciseRepository(directory_path=exercise_data_path)


@injectable
def make_pose_repository(
    pose_data_path: Annotated[str, Inject(config="pose_data_path")],
) -> PoseRepository:
    return JsonPoseRepository(directory_path=pose_data_path)
