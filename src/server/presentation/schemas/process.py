from typing import List

from pydantic import BaseModel


class EmgSensor(BaseModel):
    sensor_name: str
    zone: str


class ProcessRequest(BaseModel):
    landmarks: List[List[float]]
    emgs: List[EmgSensor]
