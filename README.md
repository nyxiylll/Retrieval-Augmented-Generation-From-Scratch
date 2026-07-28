# Retrieval-Augmented Generation From Scratch

A clean, from-scratch implementation of a RAG pipeline in Python — no LangChain, no LlamaIndex, just the raw building blocks.

## What it does

Loads documents (`.txt` or `.pdf`), chunks them, embeds the chunks into a local vector database using [ChromaDB](https://www.trychroma.com/), and answers questions over them using a Groq-hosted LLM (Llama 3.3 70B by default).

## Project layout

```
src/core/
├── document.py      # Document dataclass
├── exception.py     # Custom exception hierarchy
├── loader.py        # TextLoader, PDFLoader, load_file()
├── splitter.py      # CharacterSplitter, SentenceSplitter
├── vectorstore.py   # Embedding + ChromaDB wrapper
├── llm.py           # BaseLLM, GroqLLM
└── pipeline.py      # RAGPipeline (retrieval → generation)
main.py              # CLI entry point
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -e .
   ```

   Or with [uv](https://github.com/astral-sh/uv):

   ```bash
   uv sync
   ```

2. **Set your Groq API key**

   Create a free account at [console.groq.com](https://console.groq.com), grab an API key, then add it to `.env`:

   ```
   GROQ_API_KEY=gsk_...
   ```

3. **Run**

   Without a file (uses built-in sample text about RAG):

   ```bash
   python main.py
   ```

   With your own file:

   ```bash
   python main.py path/to/document.pdf
   python main.py path/to/document.txt
   ```

## Example

```
You: What is RAG?
Assistant: RAG stands for Retrieval-Augmented Generation. It is a hybrid AI technique
that improves the accuracy of language models by grounding responses in external
knowledge retrieved at query time...

Sources:
  • sample
```

## How it works

1. **Load** — `TextLoader` or `PDFLoader` reads the file into `Document` objects (one per page for PDFs).
2. **Split** — `SentenceSplitter` (or `CharacterSplitter`) breaks documents into overlapping chunks.
3. **Embed & Store** — `SentenceTransformer` encodes each chunk; `ChromaDB` persists the vectors locally.
4. **Retrieve** — The user's question is embedded and a cosine-similarity search returns the top-k chunks.
5. **Generate** — The retrieved chunks are injected into a prompt and sent to Groq's API; the answer is streamed back.
