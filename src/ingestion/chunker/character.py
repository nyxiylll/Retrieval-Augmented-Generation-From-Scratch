from abc import ABC, abstractmethod
from src.core.document import Document
from src.ingestion.chunker.base import BaseSplitter
import logging

logger = logging.getLogger(__name__)

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

if __name__ == "__main__":
    document = Document(
        content = "alskdjjjjjjjjjjjjjjjjjjjjjjjjkdnlaknlianwdoinanadbnwlawndnalwkndlkn akwnd akwnld alknd alknd nalnd " \
        "nlwadlndla nnald knand alk nn lakndlka ndl alkndalknd landandklnnn lknlkn n ibiub uibl ui lib iub ubbu ub",
        metadata = {
            "name" : "Aman"
        }
    )
    splitter = CharacterSplitter(10,1)
    chunks = splitter.split([document])
    print(len(chunks))