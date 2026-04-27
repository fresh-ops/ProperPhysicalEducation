from pydantic import BaseModel


class ExerciseRequest(BaseModel):
    id: int


class ExerciseItem(BaseModel):
    id: int
    name: str


class ExercisesResponse(BaseModel):
    exercises: list[ExerciseItem]
