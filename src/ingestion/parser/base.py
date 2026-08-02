from abc import ABC , abstractmethod
from src.core import Document

class BaseLoader(ABC):

    @abstractmethod
    def load(self) -> list[Document]:
        pass
