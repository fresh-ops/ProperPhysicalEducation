from domain.model.emg import EmgReading
from domain.model.zone import Zone
from application.processor.process_context import ProcessContext
from presentation.schemas.process import ProcessRequest
from domain.service.pose.skeleton_transformer import landmarks_to_pose


def map_to_context(request: ProcessRequest) -> ProcessContext:
    pose = landmarks_to_pose(request.landmarks)
    emgs = [
        EmgReading(sensor_id=emg.sensor_name, zone=Zone(emg.zone))
        for emg in request.emgs
    ]
    return ProcessContext(pose=pose, emgs=emgs)
