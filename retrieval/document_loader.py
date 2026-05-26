"""
retrieval/document_loader.py
-----------------------------
Loads documents from the data/docs directory.
Supports: .txt, .md, .pdf files.
"""

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from config.settings import DOCS_DIR


def load_all_documents() -> list[Document]:
    """
    Walk the DOCS_DIR and load every supported file.
    Returns a flat list of LangChain Document objects.
    """
    docs: list[Document] = []
    docs_path = Path(DOCS_DIR)

    if not docs_path.exists():
        print(f"[DocumentLoader] DOCS_DIR not found: {docs_path}")
        return docs

    for file_path in docs_path.rglob("*"):
        if file_path.suffix.lower() in (".txt", ".md"):
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                loaded = loader.load()
                # Tag each doc with its source file
                for doc in loaded:
                    doc.metadata["source"] = str(file_path.name)
                docs.extend(loaded)
                print(f"[DocumentLoader] Loaded: {file_path.name} ({len(loaded)} doc(s))")
            except Exception as e:
                print(f"[DocumentLoader] Error loading {file_path.name}: {e}")

        elif file_path.suffix.lower() == ".pdf":
            try:
                loader = PyPDFLoader(str(file_path))
                loaded = loader.load()
                for doc in loaded:
                    doc.metadata["source"] = str(file_path.name)
                docs.extend(loaded)
                print(f"[DocumentLoader] Loaded PDF: {file_path.name} ({len(loaded)} page(s))")
            except Exception as e:
                print(f"[DocumentLoader] Error loading PDF {file_path.name}: {e}")

    print(f"[DocumentLoader] Total documents loaded: {len(docs)}")
    return docs
