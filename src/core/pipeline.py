from src.core.document import Document
from src.database.vectorstore import VectorStore
from src.llm.groq import BaseLLM
from src.core.exception import PipelineError
import logging

logger = logging.getLogger(__name__)

DEFAULT_PROMPT_TEMPLATE = """You are a helpful assistant. Answer the question below using only the provided context.
If the context does not contain enough information to answer, say so clearly.

Context:
{context}

Question:
{question}

Answer:"""


class RAGPipeline:

    def __init__(
        self,
        retriever: VectorStore,
        llm: BaseLLM,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
    ):
        self.retriever = retriever
        self.llm = llm
        self.prompt_template = prompt_template

    def run(self, question: str) -> dict:
        if not question.strip():
            raise PipelineError("Question cannot be empty")

        retrieved_docs: list[Document] = self.retriever.search(question)

        if not retrieved_docs:
            logger.warning("No documents retrieved for query: %s", question)
            return {
                "question": question,
                "answer": "I could not find any relevant information in the knowledge base.",
                "sources": [],
            }

        context = "\n\n---\n\n".join(doc.content for doc in retrieved_docs)
        prompt = self.prompt_template.format(context=context, question=question)
        answer = self.llm.generate(prompt)

        sources = []
        for doc in retrieved_docs:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            entry = {"source": source}
            if page is not None:
                entry["page"] = page
            if entry not in sources:
                sources.append(entry)

        logger.info("Pipeline answered question with %d source(s)", len(sources))

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
