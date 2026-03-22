from pydantic import BaseModel


class ExerciseRequest(BaseModel):
    id: int
