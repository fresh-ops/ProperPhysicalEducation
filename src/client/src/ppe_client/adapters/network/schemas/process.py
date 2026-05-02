from pydantic import BaseModel


class EmgSensor(BaseModel):
    sensor_name: str
    zone: str


class ProcessRequest(BaseModel):
    landmarks: list[list[float]]
    emgs: list[EmgSensor]
