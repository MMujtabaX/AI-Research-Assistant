"""
agents/retriever_agent.py
--------------------------
Agent #2 — Retriever Agent

Responsibility:
  Executes the research plan from the Planner Agent:
    - Searches the FAISS vector store (RAG)
    - Fetches news via NewsAPI
    - Fetches books via Open Library API
    - Reads local notes via Filesystem MCP
    - Logs everything via SQLite MCP

Output: A rich context dict that the Synthesizer Agent will use.
"""

from langchain_community.vectorstores import FAISS

from api_tools.news_api import NewsAPIClient
from api_tools.open_library_api import OpenLibraryClient
from mcp_tools.filesystem_mcp import FilesystemMCPServer
from retrieval.vector_store import search_vector_store


class RetrieverAgent:
    """
    Retriever Agent: Executes the plan and gathers context from all sources.
    """

    def __init__(self, vector_store: FAISS):
        self.vector_store = vector_store
        self.news_client = NewsAPIClient()
        self.library_client = OpenLibraryClient()
        self.fs_mcp = FilesystemMCPServer()

    def retrieve(self, query: str, plan: dict) -> dict:
        """
        Execute all retrieval steps defined in the plan.

        Args:
            query: Original user query
            plan:  Structured plan from PlannerAgent

        Returns:
            context dict with:
              - rag_results: list of Document objects
              - news_text: formatted news string
              - books_text: formatted books string
              - local_notes: content of research_notes.txt
              - sources_used: list of source names
        """
        print(f"\n[RetrieverAgent] Executing retrieval plan...")
        search_terms = plan.get("search_terms", [query])
        primary_term = search_terms[0] if search_terms else query

        context = {
            "rag_results": [],
            "news_text": "",
            "books_text": "",
            "local_notes": "",
            "sources_used": [],
        }

        # ── 1. RAG — Vector Store Search ──────────────────────────────────
        if plan.get("use_local_docs", False):
            print("[RetrieverAgent] Searching vector store...")
            try:
                rag_docs = search_vector_store(self.vector_store, primary_term)
                context["rag_results"] = rag_docs
                context["sources_used"].append("local_vector_store")
                print(f"[RetrieverAgent] RAG: {len(rag_docs)} chunk(s) retrieved")
            except Exception as e:
                print(f"[RetrieverAgent] RAG error: {e}")

        # ── 2. News API ────────────────────────────────────────────────────
        if plan.get("use_news_api", False):
            print("[RetrieverAgent] Fetching news...")
            articles = self.news_client.search(primary_term, max_results=4)
            context["news_text"] = self.news_client.format_for_agent(articles)
            if articles:
                context["sources_used"].append("news_api")

        # ── 3. Open Library API ────────────────────────────────────────────
        if plan.get("use_books_api", False):
            print("[RetrieverAgent] Searching Open Library...")
            books = self.library_client.search_books(primary_term, max_results=4)
            context["books_text"] = self.library_client.format_for_agent(books)
            if books:
                context["sources_used"].append("open_library_api")

        # ── 4. Filesystem MCP — Local Notes ───────────────────────────────
        print("[RetrieverAgent] Reading local notes via Filesystem MCP...")
        notes_result = self.fs_mcp.read_file("research_notes.txt")
        if notes_result["success"] and notes_result["content"]:
            context["local_notes"] = notes_result["content"]
            context["sources_used"].append("filesystem_mcp")

        print(f"[RetrieverAgent] Done. Sources used: {context['sources_used']}")
        return context

    def format_rag_results(self, rag_docs: list) -> str:
        """Convert RAG Document objects into readable text for the synthesizer."""
        if not rag_docs:
            return "No relevant passages found in local documents."

        lines = ["📄 Relevant passages from local documents:\n"]
        for i, doc in enumerate(rag_docs, 1):
            source = doc.metadata.get("source", "unknown")
            lines.append(f"{i}. [Source: {source}]\n{doc.page_content}\n")
        return "\n".join(lines)
