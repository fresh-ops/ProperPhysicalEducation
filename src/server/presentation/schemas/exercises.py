from pydantic import BaseModel


class ExerciseItem(BaseModel):
    id: int
    name: str


class ExercisesResponse(BaseModel):
    exercises: list[ExerciseItem]
