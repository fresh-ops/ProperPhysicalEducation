from pydantic import BaseModel


class FeedbackItem(BaseModel):
    type: str
    message: str


class FeedbackResponse(BaseModel):
    feedbacks: list[FeedbackItem]
