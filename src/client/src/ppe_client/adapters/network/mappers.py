from ppe_client.adapters.network.schemas.feedback import FeedbackResponse
from ppe_client.application.feedback import Feedback, FeedbackType


def map_to_list(schema: FeedbackResponse) -> list[Feedback]:
    items = [
        Feedback(type=FeedbackType(item.type), message=item.message)
        for item in schema.feedbacks
    ]
    return items
