from abc import ABC, abstractmethod
from src.core.document import Document
import logging

logger = logging.getLogger(__name__)


class BaseSplitter(ABC):

    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        pass


class CharacterSplitter(BaseSplitter):

    def __init__(self, chunk_size: int, chunk_overlap: int = 0):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        chunks = []
        skipped = 0

        for doc in documents:
            content = doc.content or ""

            if not content.strip():
                skipped += 1
                continue

            start = 0
            chunk_index = 0
            content_length = len(content)
            step = self.chunk_size - self.chunk_overlap

            while start < content_length:
                end = min(start + self.chunk_size, content_length)
                text = content[start:end]

                chunks.append(
                    Document(
                        content=text,
                        metadata={
                            **doc.metadata,
                            "chunk_index": chunk_index,
                            "start_char": start,
                            "end_char": end,
                        },
                    )
                )

                chunk_index += 1
                start += step

        if skipped:
            logger.warning("Skipped %d empty documents during splitting", skipped)

        logger.info("Produced %d chunks from %d documents", len(chunks), len(documents))
        return chunks


class SentenceSplitter(BaseSplitter):

    def __init__(self, chunk_size: int, chunk_overlap: int = 1):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        import re

        chunks = []
        skipped = 0

        sentence_pattern = re.compile(r"(?<=[.!?])\s+")

        for doc in documents:
            content = doc.content or ""

            if not content.strip():
                skipped += 1
                continue

            sentences = sentence_pattern.split(content.strip())
            sentences = [s.strip() for s in sentences if s.strip()]

            current_chars = 0
            current_sentences: list[str] = []
            chunk_index = 0
            start_char = 0

            for sentence in sentences:
                sentence_len = len(sentence)

                if current_chars + sentence_len > self.chunk_size and current_sentences:
                    text = " ".join(current_sentences)
                    end_char = start_char + len(text)

                    chunks.append(
                        Document(
                            content=text,
                            metadata={
                                **doc.metadata,
                                "chunk_index": chunk_index,
                                "start_char": start_char,
                                "end_char": end_char,
                            },
                        )
                    )

                    chunk_index += 1
                    overlap = current_sentences[-self.chunk_overlap :] if self.chunk_overlap else []
                    start_char = end_char + 1
                    current_sentences = overlap
                    current_chars = sum(len(s) for s in current_sentences)

                current_sentences.append(sentence)
                current_chars += sentence_len

            if current_sentences:
                text = " ".join(current_sentences)
                chunks.append(
                    Document(
                        content=text,
                        metadata={
                            **doc.metadata,
                            "chunk_index": chunk_index,
                            "start_char": start_char,
                            "end_char": start_char + len(text),
                        },
                    )
                )

        if skipped:
            logger.warning("Skipped %d empty documents during splitting", skipped)

        logger.info("Produced %d chunks from %d documents", len(chunks), len(documents))
        return chunks
