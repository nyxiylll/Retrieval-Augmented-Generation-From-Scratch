from abc import ABC, abstractmethod
from pathlib import Path
from charset_normalizer import from_path
from src.core.document import Document
from src.core.exception import LoaderError
import logging
import fitz

logger = logging.getLogger(__name__)


class BaseLoader(ABC):

    @abstractmethod
    def load(self) -> list[Document]:
        pass


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


class PDFLoader(BaseLoader):

    MAX_FILE_SIZE = 100 * 1024 * 1024

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise LoaderError(f"Path is not a file: {self.file_path}")

        if self.file_path.suffix.lower() != ".pdf":
            raise LoaderError(f"PDFLoader only accepts .pdf files, got: {self.file_path.suffix}")

        if self.file_path.stat().st_size > self.MAX_FILE_SIZE:
            raise LoaderError("PDF exceeds the 100 MB size limit")

    def load(self) -> list[Document]:
        try:
            pdf = fitz.open(self.file_path)
        except Exception as e:
            raise LoaderError(f"Could not open PDF: {self.file_path}") from e

        documents = []

        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text()

            if not text.strip():
                logger.debug("Skipping empty page %d in %s", page_num + 1, self.file_path)
                continue

            documents.append(
                Document(
                    content=text,
                    metadata={
                        "source": str(self.file_path),
                        "file_type": ".pdf",
                        "page": page_num + 1,
                        "total_pages": len(pdf),
                        "char_count": len(text),
                    },
                )
            )

        pdf.close()

        if not documents:
            logger.warning("No extractable text found in PDF: %s", self.file_path)

        logger.info("Loaded %d pages from %s", len(documents), self.file_path)
        return documents


def load_file(file_path: str | Path, **kwargs) -> list[Document]:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return PDFLoader(path).load()
    elif ext == ".txt":
        return TextLoader(path, **kwargs).load()
    else:
        raise LoaderError(f"No loader available for extension: {ext}")
