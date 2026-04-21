from typing import Annotated

from wireup import Inject, injectable

from application.mapper.pose_mapper import PoseMapper


from application.processor.camera.camera_pose_processor_factory import (
    CameraPoseProcessorFactory,
)
from domain.ports.exercise_repository import ExerciseRepository
from domain.ports.pose_repository import PoseRepository
from domain.service.pose.pose_matcher.strategy.penalty_strategy import PenaltyStrategy
from domain.service.pose.pose_matcher.strategy.pose_matcher_strategy import (
    PoseMatcherStrategy,
)

from application.processor.sensor_processor import SensorProcessorFactory
from application.mapper.process_context_mapper import ProcessContextMapper


@injectable
def make_camera_pose_processor_factory(
    exercise_repository: ExerciseRepository,
    pose_repository: PoseRepository,
    pose_matcher_strategy: PoseMatcherStrategy,
    frame_tolerance: int,
) -> CameraPoseProcessorFactory:
    return CameraPoseProcessorFactory(
        exercise_repository=exercise_repository,
        pose_repository=pose_repository,
        pose_matcher_strategy=pose_matcher_strategy,
        frame_tolerance=frame_tolerance,
    )


@injectable
def make_frame_tolerance(
    frame_tolerance: Annotated[int, Inject(config="frame_tolerance")],
) -> int:
    return frame_tolerance


@injectable
def make_pose_matcher_strategy() -> PoseMatcherStrategy:
    return PenaltyStrategy()


@injectable
def make_context_mapper(pose_mapper: PoseMapper) -> ProcessContextMapper:
    return ProcessContextMapper(pose_mapper=pose_mapper)


@injectable
def make_processor_factories(
    camera_pose_processor_factory: CameraPoseProcessorFactory,
) -> list[SensorProcessorFactory]:
    return [
        camera_pose_processor_factory,
    ]


@injectable
def make_pose_mapper() -> PoseMapper:
    return PoseMapper()
