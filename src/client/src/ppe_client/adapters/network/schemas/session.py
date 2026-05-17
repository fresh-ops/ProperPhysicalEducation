from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    exercise_id: str


class StartSessionResponse(BaseModel):
    session_id: str
