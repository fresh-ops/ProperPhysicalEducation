from dataclasses import dataclass
from typing import List


@dataclass
class FeedbackItemDto:
    type: str
    message: str


@dataclass
class FeedbackResponseDto:
    feedbacks: List[FeedbackItemDto]
