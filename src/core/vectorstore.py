from sentence_transformers import SentenceTransformer
from src.core.document import Document
import chromadb
from src.core.exception import VectorStoreError

class VectorStore:
    def __init__(self,
                 model_name : str,
                 persist_directory :str,
                 collection_name : str = "documents",
                 batch_size : int = 64):

        self.batch_size = batch_size

        try:
            self.embedding_model = SentenceTransformer(
                f"sentence-transformers/{model_name}"
            )
        except Exception as e:
            raise VectorStoreError(
                f"failed to load embeddings to the model "
            ) from e 
        
        self.client = chromadb.PersistentClient(persist_directory)
        self.collection = self.client.get_or_create_collection(
            "document"
        )
        self.top_k = None

    def as_retriever(self,k : int):
        self.top_k = k
        return self

    def add(self,chunks : list[Document]):

        valid_chunk = [c for c in chunks if c.content]

        if not valid_chunk:
            return
        

        ids = [str(i) for i in range(len(valid_chunk))]

        text = [c.content for c in  valid_chunk]

        embedding = self.embedding_model.encode(text).tolist() 

        self.collection.add(
            ids = ids,
            embeddings = embedding,
            documents = text,
            metadatas = [c.metadata for c in valid_chunk]
        )

    def search(self,query : str):

        if not self.top_k:
            raise ValueError(
                f"top_k not initilized"
                "use as_retriever to initilize"
            )
        embedded_query = self.embedding_model.encode(query).tolist()

        result = self.collection.query(
            query_embeddings = [embedded_query],
            n_results = self.top_k
        )


        docs = result["documents"][0]
        metadata = result["metadatas"][0]

        output = []

        for doc , metas in zip(docs,metadata):
            output.append(
                Document(
                    content = doc,
                    metadata = metas
                )
            )
