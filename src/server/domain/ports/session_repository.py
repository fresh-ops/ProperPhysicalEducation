from abc import ABC, abstractmethod

from domain.model.session import Session
from domain.model.session_id import SessionId


class SessionRepository(ABC):
    @abstractmethod
    def save(self, session: Session) -> SessionId:
        pass

    @abstractmethod
    def get(self, session_id: SessionId) -> Session:
        pass

    @abstractmethod
    def delete(self, session_id: SessionId) -> None:
        pass
