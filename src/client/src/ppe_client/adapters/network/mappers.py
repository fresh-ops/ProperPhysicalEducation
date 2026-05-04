from ppe_client.adapters.network.schemas.feedback import FeedbackResponse
from ppe_client.adapters.network.schemas.process import EmgSensor, ProcessRequest
from ppe_client.adapters.poses.pose_converter import PoseConverter
from ppe_client.application.feedback import Feedback, FeedbackType
from ppe_client.application.process_data import ProcessData


def map_to_list(data: FeedbackResponse) -> list[Feedback]:
    items = [
        Feedback(type=FeedbackType(item.type), message=item.message)
        for item in data.feedbacks
    ]
    return items


def map_to_schema(data: ProcessData) -> ProcessRequest:
    landmarks = PoseConverter.to_list(data.pose)
    emgs = [
        EmgSensor(sensor_name=emg.sensor_name, zone=emg.zone.value) for emg in data.emgs
    ]
    return ProcessRequest(landmarks=landmarks, emgs=emgs)
