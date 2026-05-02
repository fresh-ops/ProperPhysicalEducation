from typing import List

from pydantic import BaseModel


class ProcessRequest(BaseModel):
    landmarks: List[List[float]]
