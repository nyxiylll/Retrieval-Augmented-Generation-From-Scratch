from abc import ABC, abstractmethod
from pathlib import Path
from charset_normalizer import from_path
from src.core.document import Document
from src.core.exception import LoaderError
from src.ingestion.parser.base import BaseLoader
import logging
import fitz

logger = logging.getLogger(__name__)


class TextLoader(BaseLoader):

    SUPPORTED_TYPES = {".txt"}
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(
        self,
        file_path: str | Path,
        encoding: str | None = None,
        auto_detect: bool = False,
    ):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.auto_detect = auto_detect

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise LoaderError(f"Path is not a file: {self.file_path}")

        if self.file_path.suffix.lower() not in self.SUPPORTED_TYPES:
            raise LoaderError(f"Unsupported file type: {self.file_path.suffix}")

        if self.file_path.stat().st_size > self.MAX_FILE_SIZE:
            raise LoaderError("File exceeds the 50 MB size limit")

    def load(self) -> list[Document]:
        encoding = self.encoding or "utf-8"

        try:
            text = self._read(encoding)
        except (UnicodeDecodeError, LookupError) as e:
            if not self.auto_detect:
                raise LoaderError(
                    f"Failed to decode {self.file_path} using {encoding}"
                ) from e

            encoding = self._detect_encoding()

            try:
                text = self._read(encoding)
            except (UnicodeDecodeError, LookupError) as e2:
                raise LoaderError(
                    f"Auto-detected encoding '{encoding}' still failed on {self.file_path}"
                ) from e2
        except OSError as e:
            raise LoaderError(f"OS error reading {self.file_path}") from e

        if not text.strip():
            logger.warning("Loaded file is empty: %s", self.file_path)

        return [
            Document(
                content=text,
                metadata={
                    "source": str(self.file_path),
                    "file_type": self.file_path.suffix.lower(),
                    "encoding": encoding,
                    "char_count": len(text),
                },
            )
        ]

    def _read(self, encoding: str) -> str:
        with open(self.file_path, "r", encoding=encoding) as f:
            return f.read()

    def _detect_encoding(self) -> str:
        result = from_path(self.file_path).best()
        if not result:
            raise LoaderError(f"Could not detect encoding for {self.file_path}")
        return result.encoding


if __name__ == "__main__":
    loader = TextLoader(
        file_path = "./text.txt"
    )

    text_document = loader.load()

    print(text_document[0].content)