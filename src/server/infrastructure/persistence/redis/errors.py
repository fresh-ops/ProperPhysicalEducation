from domain.ports.errors import RepositoryError


class RedisRepositoryError(RepositoryError):
    pass


class RedisConnectionError(RedisRepositoryError):
    def __init__(self, original_exception: Exception):
        super().__init__(f"Error connecting to Redis: {original_exception}")


class RedisOperationError(RedisRepositoryError):
    def __init__(self, operation: str, original_exception: Exception):
        super().__init__(
            f"Error during Redis operation '{operation}': {original_exception}"
        )
