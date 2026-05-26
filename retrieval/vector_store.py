"""
retrieval/vector_store.py
--------------------------
Builds and manages a FAISS vector store.
- On first run: embeds chunks and saves index to disk
- On subsequent runs: loads existing index from disk
"""

from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config.settings import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    VECTOR_STORE_DIR,
    TOP_K_RESULTS,
)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )


def build_or_load_vector_store(chunks: list[Document]) -> FAISS:
    """
    Load existing FAISS index from disk, or build a new one from chunks.

    Args:
        chunks: Pre-split Document objects to embed (used only if building fresh)

    Returns:
        A FAISS vector store ready for similarity search
    """
    index_path = Path(VECTOR_STORE_DIR)
    index_file = index_path / "index.faiss"
    embeddings = get_embeddings()

    if index_file.exists():
        print("[VectorStore] Loading existing FAISS index from disk...")
        store = FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print(f"[VectorStore] Loaded. Index contains {store.index.ntotal} vectors.")
    else:
        print(f"[VectorStore] Building new FAISS index from {len(chunks)} chunks...")
        if not chunks:
            raise ValueError("No chunks provided to build vector store. Add docs to data/docs/")
        store = FAISS.from_documents(chunks, embeddings)
        store.save_local(str(index_path))
        print(f"[VectorStore] Saved to {index_path}. Vectors: {store.index.ntotal}")

    return store


def search_vector_store(store: FAISS, query: str) -> list[Document]:
    """
    Run a similarity search and return top-K most relevant chunks.

    Args:
        store: The loaded FAISS store
        query: The search query string

    Returns:
        List of matching Document objects
    """
    results = store.similarity_search(query, k=TOP_K_RESULTS)
    print(f"[VectorStore] Query: '{query[:60]}...' → {len(results)} result(s)")
    return results


def add_documents_to_store(store: FAISS, new_chunks: list[Document]) -> FAISS:
    """Add new chunks to an existing store and save."""
    store.add_documents(new_chunks)
    store.save_local(str(VECTOR_STORE_DIR))
    print(f"[VectorStore] Added {len(new_chunks)} new chunks. Saved.")
    return store
