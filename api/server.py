"""
api/server.py
--------------
FastAPI backend — exposes the multi-agent research system as REST endpoints.

Endpoints:
  POST /query          — Run a research query through LangGraph
  GET  /history        — Get past research sessions from SQLite
  GET  /health         — Health check
  POST /clear-memory   — Reset conversation memory
  GET  /summary        — Get conversation summary
  POST /add-document   — Upload a new document to the RAG knowledge base
  DELETE /vector-store — Rebuild the vector store from scratch
"""

import os
import sys
import shutil
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent dir to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import OPENAI_API_KEY, DOCS_DIR, VECTOR_STORE_DIR
from retrieval.document_loader import load_all_documents
from retrieval.chunker import chunk_documents
from retrieval.vector_store import build_or_load_vector_store
from graph.workflow import build_workflow
from graph.state import ResearchState
from memory.memory_manager import MemoryManager
from mcp_tools.sqlite_mcp import SQLiteMCPServer


# ── Global app state ──────────────────────────────────────────────────────
class AppState:
    graph = None
    memory: MemoryManager = None
    db: SQLiteMCPServer = None
    ready: bool = False
    status: str = "initializing"


app_state = AppState()


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the AI system on startup."""
    print("🚀 Booting AI Research Assistant...")
    try:
        docs = load_all_documents()
        chunks = chunk_documents(docs)
        vector_store = build_or_load_vector_store(chunks)
        app_state.graph = build_workflow(vector_store)
        app_state.memory = MemoryManager()
        app_state.db = SQLiteMCPServer()
        app_state.ready = True
        app_state.status = "ready"
        print("✅ System ready!")
    except Exception as e:
        app_state.status = f"error: {str(e)}"
        print(f"❌ Startup failed: {e}")
    yield
    print("👋 Shutting down...")


# ── FastAPI app ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Research Assistant API",
    description="Multi-Agent Research System with LangGraph, RAG, MCP & External APIs",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]
    plan: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    ready: bool
    message: str


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status=app_state.status,
        ready=app_state.ready,
        message="System is ready to accept queries." if app_state.ready
                else "System is still initializing or encountered an error.",
    )


@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    if not app_state.ready:
        raise HTTPException(status_code=503, detail="System is not ready yet.")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        state: ResearchState = {
            "query": request.query,
            "chat_history": app_state.memory.format_history_for_prompt(),
            "conversation_summary": app_state.memory.get_summary(),
            "plan": None,
            "context": None,
            "final_answer": None,
            "error": None,
            "needs_clarification": False,
        }

        final_state = app_state.graph.invoke(state)
        answer = final_state.get("final_answer", "No answer generated.")
        sources = (final_state.get("context") or {}).get("sources_used", [])
        plan = final_state.get("plan")

        app_state.memory.save_turn(request.query, answer)

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            plan=plan,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 10):
    if not app_state.db:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    result = app_state.db.get_recent_sessions(limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return {"sessions": result["sessions"]}


@app.get("/summary")
async def get_summary():
    if not app_state.memory:
        raise HTTPException(status_code=503, detail="Memory not initialized.")
    return {
        "summary": app_state.memory.get_summary() or "No conversation yet.",
        "recent_turns": app_state.memory.format_history_for_prompt(),
    }


@app.post("/clear-memory")
async def clear_memory():
    if app_state.memory:
        app_state.memory.clear()
    return {"message": "Memory cleared successfully."}


@app.post("/add-document")
async def add_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    allowed = {".txt", ".md", ".pdf"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"Only {allowed} files supported.")

    dest = Path(DOCS_DIR) / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Rebuild vector store in background
    background_tasks.add_task(_rebuild_vector_store)
    return {"message": f"'{file.filename}' uploaded. Rebuilding knowledge base in background..."}


async def _rebuild_vector_store():
    """Background task to rebuild FAISS after new doc upload."""
    try:
        vs_path = Path(VECTOR_STORE_DIR)
        if vs_path.exists():
            shutil.rmtree(vs_path)
        docs = load_all_documents()
        chunks = chunk_documents(docs)
        vector_store = build_or_load_vector_store(chunks)
        app_state.graph = build_workflow(vector_store)
        print("✅ Vector store rebuilt successfully.")
    except Exception as e:
        print(f"❌ Rebuild failed: {e}")


@app.delete("/vector-store")
async def reset_vector_store(background_tasks: BackgroundTasks):
    background_tasks.add_task(_rebuild_vector_store)
    return {"message": "Rebuilding vector store from scratch in background..."}


@app.get("/search-history")
async def search_history(keyword: str):
    if not app_state.db:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    result = app_state.db.search_sessions(keyword)
    return {"sessions": result.get("sessions", [])}