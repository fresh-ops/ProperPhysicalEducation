from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    session_timeout_seconds: int = 60
    exercise_data_path: str = "data/exercise"
    pose_data_path: str = "data/pose"
    frame_tolerance: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
