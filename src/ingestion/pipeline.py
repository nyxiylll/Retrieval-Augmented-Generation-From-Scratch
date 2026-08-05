from pathlib import Path

from src.ingestion.parser.text import TextLoader
from src.ingestion.parser.pdf import PDFLoader
from src.ingestion.chunker.character import CharacterSplitter
from src.database.vectorstore import ChromaVectorStore


class IngestionPipeline:

    def __init__(
        self,
        file_path: str | Path,
        chunk_size: int,
        chunk_overlap: int,
        model_name: str,
        persist_directory: str,
        collection_name: str,
        batch_size: int,
        auto_encoding: bool = True,
    ):

        self.file_path = Path(file_path)

        if self.file_path.suffix.lower() == ".txt":
            self.loader = TextLoader(
                file_path=self.file_path, auto_detect=auto_encoding
            )

        elif self.file_path.suffix.lower() == ".pdf":
            self.loader = PDFLoader(file_path=self.file_path)

        else:
            raise ValueError(f"Unsupported file type: {self.file_path.suffix}")

        self.splitter = CharacterSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        self.vector_store = ChromaVectorStore(
            model_name=model_name,
            persist_directory=persist_directory,
            collection_name=collection_name,
            batch_size=batch_size,
        )

    def _load(self):
        
        try:
            return self.loader.load()
            

        except Exception as e:
            raise RuntimeError(f"Failed to load document: {e}")

    def _convert_chunks(self, documents):
        
        return self.splitter.split(documents)

    def _store_in_vectorstore(self, chunks):
        
        try:
            self.vector_store.add(chunks)

        except Exception as e:
            raise RuntimeError(f"Failed storing chunks: {e}")

    def invoke(self):
        

        documents = self._load()

        chunks = self._convert_chunks(documents)

        self._store_in_vectorstore(chunks)

        return "Done"


if __name__ == "__main__":

    pipeline = IngestionPipeline(
        file_path="text.txt",
        chunk_size=100,
        chunk_overlap=10,
        model_name="all-MiniLM-L6-v2",
        persist_directory="./chroma_db",
        collection_name="documents",
        batch_size = 64
    )

    done = pipeline.invoke()
    print(done)
