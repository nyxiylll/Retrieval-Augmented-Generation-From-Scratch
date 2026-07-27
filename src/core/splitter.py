from abc import ABC , abstractmethod
from src.core.document import Document

import logging 

logger = logging.getLogger(__name__)


class BaseSplitter(ABC):

    @abstractmethod
    def split(self):
        pass


class CharacterSplitter(BaseSplitter) :
    def __init__(self,
                 chunk_size : int,
                 chunk_overlap : int  = 0):

        if chunk_size <= 0:
            raise ValueError(
                f"Chunk size must be a positive Value"
            )

        if chunk_overlap < 0:
                    raise ValueError(
                        f"Chunk overlap must be a positive Value"
                    )

        if chunk_size <= chunk_overlap:
            raise ValueError(
                f"ChunkOverlap cannot be greater than chunk size"
            )

        self.chunk_size = chunk_size 
        self.chunk_overlap = chunk_overlap 

    def split(self,documents : list[Document]):
        chunks = []
        skipped = 0

        for doc in documents:

            content = doc.content or ""

            if len(doc.content) < 1:
                skipped += 1
                continue 

            current_chunk_length = len(doc.content)
            start = 0
            chunk_index = 0

            while start < current_chunk_length:
                end = start  + self.chunk_size
                text = doc.content[start:end]

                chunks.append(
                    Document(
                        content = text,
                        metadata = {
                             **doc.metadata,
                             "chunk_index" : chunk_index,
                             "start_char" : start,
                             "end_char" : min(end,current_chunk_length)
                        }
                    )
                )
                chunk_index += 1
                start += self.chunk_size - self.chunk_overlap
            if skipped:
                 logger.warning(f"Split {len(documents) - skipped} into {len(chunks)}")

        return chunks


