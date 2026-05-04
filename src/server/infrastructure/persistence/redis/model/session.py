from pydantic import BaseModel


class RedisSession(BaseModel):
    session_id: str
    exercise_id: str
    current_pose_index: int
    frame_tolerance_counter: int
