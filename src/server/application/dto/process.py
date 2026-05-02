from dataclasses import dataclass
from typing import List


@dataclass
class ProcessRequestDto:
    landmarks: List[List[float]]
