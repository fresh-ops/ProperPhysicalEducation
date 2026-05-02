from abc import ABC, abstractmethod

from domain.model.session import Session
from domain.model.session_id import SessionId


class SessionRepository(ABC):
    @abstractmethod
    async def create(self, session: Session) -> SessionId:
        pass

    @abstractmethod
    async def update(self, session: Session) -> SessionId:
        pass

    @abstractmethod
    async def get(self, session_id: SessionId) -> Session:
        pass

    @abstractmethod
    async def delete(self, session_id: SessionId) -> None:
        pass
