from domain.model.exercise_id import ExerciseId
from domain.model.exercise_state import ExerciseState
from domain.model.session import Session
from domain.model.session_id import SessionId
from infrastructure.persistence.redis.model.session import RedisSession


class SessionMapper:
    @staticmethod
    def map_to(session: Session) -> RedisSession:
        return RedisSession(
            session_id=session.session_id.id,
            exercise_id=session.exercise_id.id,
            current_pose_index=session.exercise_state.current_pose_index,
            frame_tolerance_counter=session.exercise_state.frame_tolerance_counter,
        )

    @staticmethod
    def map_from(data: RedisSession) -> Session:
        return Session(
            session_id=SessionId(data.session_id),
            exercise_id=ExerciseId(data.exercise_id),
            exercise_state=ExerciseState(
                current_pose_index=data.current_pose_index,
                frame_tolerance_counter=data.frame_tolerance_counter,
            ),
        )
