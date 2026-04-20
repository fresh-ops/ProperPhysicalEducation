from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    session_timeout_seconds: int = 60
    exercise_data_path: str = "infrastructure/data/json/exercise"
    pose_data_path: str = "infrastructure/data/json/pose"
    frame_tolerance: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
