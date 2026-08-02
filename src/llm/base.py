from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
