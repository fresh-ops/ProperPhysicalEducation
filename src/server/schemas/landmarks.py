from typing import List

from pydantic import BaseModel


class LandmarksRequest(BaseModel):
    landmarks: List[List[float]]
