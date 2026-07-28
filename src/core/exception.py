class RAGException(Exception):
    pass


class LoaderError(RAGException):
    pass


class VectorStoreError(RAGException):
    pass


class LLMError(RAGException):
    pass


class PipelineError(RAGException):
    pass