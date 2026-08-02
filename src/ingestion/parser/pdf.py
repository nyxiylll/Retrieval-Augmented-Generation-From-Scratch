from abc import ABC, abstractmethod
from pathlib import Path
from charset_normalizer import from_path
from src.core import Document
from src.core.exception import LoaderError
from src.ingestion.parser.base import BaseLoader
import logging
import fitz

logger = logging.getLogger(__name__)


class PDFLoader(BaseLoader):

    MAX_FILE_SIZE = 100 * 1024 * 1024

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise LoaderError(f"Path is not a file: {self.file_path}")

        if self.file_path.suffix.lower() != ".pdf":
            raise LoaderError(
                f"PDFLoader only accepts .pdf files, got: {self.file_path.suffix}"
            )

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
                logger.debug(
                    "Skipping empty page %d in %s", page_num + 1, self.file_path
                )
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


if __name__ == "__main__":
    loader = PDFLoader(
        file_path = "./HowTo larove it.pdf"
    )
    docs = loader.load()
    for doc in docs:
        print(doc.content)
