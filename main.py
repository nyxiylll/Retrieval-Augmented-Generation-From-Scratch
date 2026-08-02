import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.parser.loader import load_file
from src.ingestion.chunker.splitter import SentenceSplitter
from src.database.vectorstore import VectorStore
from src.llm.groq import GroqLLM
from src.core.pipeline import RAGPipeline

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

SAMPLE_TEXT = """
Retrieval-Augmented Generation (RAG) is a hybrid AI technique that improves the accuracy and
reliability of large language models by grounding their responses in external knowledge.
Instead of relying purely on knowledge baked into model weights during training, RAG dynamically
retrieves relevant documents from a knowledge base at query time and feeds them as context to
the language model before it generates an answer.

The RAG pipeline typically consists of three stages. First, documents are loaded and pre-processed
from sources such as PDFs, text files, or databases. Second, those documents are split into smaller
chunks and converted into dense vector representations called embeddings, which are stored in a
vector database. Third, when a user asks a question, the question is also embedded and used to
perform a semantic similarity search against the stored chunks. The most relevant chunks are
retrieved and injected into a prompt alongside the original question, allowing the LLM to generate
a grounded, factual response.

RAG was introduced by researchers at Meta AI in a 2020 paper titled "Retrieval-Augmented Generation
for Knowledge-Intensive NLP Tasks". It has since become the dominant pattern for building production
AI systems that require up-to-date, verifiable, and domain-specific knowledge — ranging from
enterprise search and customer support to code assistants and medical Q&A systems.

The key advantages of RAG over pure fine-tuning are that it does not require retraining the model
when new information becomes available, it naturally cites its sources, and it keeps the knowledge
base decoupled from the model weights, which dramatically reduces the cost of keeping the system
current.
"""


def ingest(store: VectorStore, file_path: Path | None = None) -> None:
    if file_path and file_path.exists():
        logger.info("Loading documents from %s", file_path)
        docs = load_file(file_path)
    else:
        logger.info("No input file provided — using built-in sample text")
        from src.core.document import Document
        docs = [Document(content=SAMPLE_TEXT.strip(), metadata={"source": "sample"})]

    splitter = SentenceSplitter(chunk_size=500, chunk_overlap=1)
    chunks = splitter.split(docs)

    logger.info("Ingesting %d chunks into vector store...", len(chunks))
    store.add(chunks)


def interactive_loop(pipeline: RAGPipeline) -> None:
    print("\n" + "=" * 60)
    print("  RAG From Scratch — interactive Q&A")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 60 + "\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        result = pipeline.run(question)
        print(f"\nAssistant: {result['answer']}")

        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                line = f"  • {s['source']}"
                if "page" in s:
                    line += f"  (page {s['page']})"
                print(line)

        print()


def main() -> None:
    file_path: Path | None = None

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            logger.error("File not found: %s", file_path)
            sys.exit(1)

    store = VectorStore(
        model_name="all-MiniLM-L6-v2",
        persist_directory="./chroma_db",
        collection_name="rag_demo",
    )

    if store.count() == 0 or file_path:
        if file_path:
            store.clear()
        ingest(store, file_path)
    else:
        logger.info("Vector store already has %d chunks — skipping ingestion", store.count())

    retriever = store.as_retriever(k=4)
    llm = GroqLLM(model="llama-3.3-70b-versatile", temperature=0.2)
    pipeline = RAGPipeline(retriever=retriever, llm=llm)

    interactive_loop(pipeline)


if __name__ == "__main__":
    main()
