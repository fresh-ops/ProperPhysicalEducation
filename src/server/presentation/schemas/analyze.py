from typing import List

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    landmarks: List[List[float]]
    emg_value: float
