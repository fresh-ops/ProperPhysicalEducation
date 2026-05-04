from pydantic import BaseModel


class ExerciseItem(BaseModel):
    exercise_id: str
    name: str


class ExercisesResponse(BaseModel):
    exercises: list[ExerciseItem]
