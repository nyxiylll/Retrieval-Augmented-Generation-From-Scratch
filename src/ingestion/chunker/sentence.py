from abc import ABC, abstractmethod
from src.core.document import Document
from src.ingestion.chunker.base import BaseSplitter
import logging

logger = logging.getLogger(__name__)


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
                    overlap = (
                        current_sentences[-self.chunk_overlap :]
                        if self.chunk_overlap
                        else []
                    )
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


if __name__ == "__main__":
    document = Document(
        content="alskdjjjjjjjj. jjjjjjjj.jjjjjjjjkdnlaknlianwdoinanadb.nwlawndnalwkndlkn akwnd akwnld alknd alknd nalnd "
        "nlwadlndla . nnald knand alk n.n lakndlka ndl alkndalknd landandklnnn. lknlkn n ibiub uibl ui lib iub ubbu ub",
        metadata={"name": "Aman"},
    )
    splitter = SentenceSplitter(10, 1)
    chunks = splitter.split([document])
    for chunk in chunks:
        print(chunk)
    print(len(chunk))
    print(chunk.metadata["chunk_index"])
