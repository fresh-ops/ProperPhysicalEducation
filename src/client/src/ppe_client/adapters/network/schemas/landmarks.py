from pydantic import BaseModel


class LandmarksRequest(BaseModel):
    landmarks: list[list[float]]
