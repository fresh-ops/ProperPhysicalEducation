from application.dto.process import ProcessRequestDto
from domain.model.pose import Pose
from domain.service.pose.skeleton_transformer import landmarks_to_pose


class PoseMapper:
    @staticmethod
    def from_dto(dto: ProcessRequestDto) -> Pose:
        return landmarks_to_pose(dto.landmarks)
