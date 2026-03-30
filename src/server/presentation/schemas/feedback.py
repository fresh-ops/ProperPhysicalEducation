from typing import List

from pydantic import BaseModel


class FeedbackItem(BaseModel):
    message: str


class FeedbackResponse(BaseModel):
    feedbacks: List[FeedbackItem]
