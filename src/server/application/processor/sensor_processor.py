from abc import ABC, abstractmethod

from domain.model.feedback import Feedback


class SensorProcessor[T](ABC):
    @abstractmethod
    def process(self, data: T) -> list[Feedback]:
        pass
