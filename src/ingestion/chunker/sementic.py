from abc import ABC, abstractmethod
from src.core.document import Document
from src.ingestion.chunker.base import BaseSplitter
from sentence_transformers import SentenceTransformer
from src.ingestion.chunker.sentence import SentenceSplitter
from dataclasses import dataclass
from typing import Dict , Any
import logging
import numpy as np 

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingStore:
    embeddings : list[int]
    content : Dict[str,Any]

class SemanticSplitter(BaseSplitter):

    """
    Documentation:

        """

    def __init__(self,
                model_name : str,
                chunk_size : int,
                chunk_overlap : int = 1,
                cosine_threshold : float = 0.85):

        try: 
            self.sentence_transformer = SentenceTransformer(
                model_name_or_path = f"sentence-transformers/{model_name}"
            )
        except:
            raise ValueError(
                f"Cannot load {model_name} using sentence-transformer"
            )
        self.splitter = SentenceSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )
        self.threshold = cosine_threshold


    def split(self,documents : list[Document]):

        chunks = []

        embedded_splits = []

        splits = self.splitter.split(
            documents = documents
        )

        for i , sentence in enumerate(splits):

            vector_embeddings = self.sentence_transformer.encode(
                sentence.content
            ).tolist()

            embedded_splits.append(EmbeddingStore(
                embeddings = vector_embeddings,
                content = {
                    "index" : i,
                    "chunk_index" : sentence.metadata["chunk_index"],
                    "text" : sentence.content,
                    "metdata" : sentence.metadata
                }
            ))

        left , right = 0 , 1 
        text = "\n"
        while right < len(embedded_splits):


            left_vectors = embedded_splits[left].embeddings
            right_vectors = embedded_splits[right].embeddings

            text.join(embedded_splits[left].metadata["text"])

            while True:

                score = np.dot(left_vectors,right_vectors)


                if score >= self.threshold:
                    text.join(embedded_splits[right].content["text"])
                    right += 1
                else:
                    metadata = embedded_splits[left].content["metadata"]
                    metadata["sentence_from"] = left
                    metadata["sentence_to"] = right
                    chunks.append(
                        Document(
                            content = text,
                            metadata = metadata
                        )
                    )
                    left = right 
                    right += 1
                    break
        return chunks





            

            



if __name__ == "__main__":
    pass