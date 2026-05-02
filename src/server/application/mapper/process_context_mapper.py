from application.dto.process import ProcessRequestDto
from application.mapper.pose_mapper import PoseMapper
from application.processor.process_context import ProcessContext


class ProcessContextMapper:
    def __init__(self, pose_mapper: PoseMapper):
        self._pose_mapper = pose_mapper

    def to_context(self, dto: ProcessRequestDto) -> ProcessContext:
        pose = self._pose_mapper.from_dto(dto)
        return ProcessContext(pose=pose)
