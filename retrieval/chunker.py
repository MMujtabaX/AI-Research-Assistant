"""
retrieval/chunker.py
---------------------
Splits raw documents into overlapping chunks for embedding.
Uses RecursiveCharacterTextSplitter for smart boundary detection.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Split a list of Documents into smaller overlapping chunks.

    Args:
        documents: Raw LangChain Document objects

    Returns:
        List of chunked Document objects with preserved metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        # Split on: paragraph breaks → sentences → words → characters
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    print(f"[Chunker] {len(documents)} document(s) → {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks
