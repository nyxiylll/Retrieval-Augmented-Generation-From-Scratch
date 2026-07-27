

class RAGException(Exception):
    pass

class LoaderError(RAGException):
    pass

class VectorStoreError(RAGException):
    pass