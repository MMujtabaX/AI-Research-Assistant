"""
config/settings.py
------------------
Central configuration. Loads .env and exposes typed settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


# ── API Keys ───────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Copy .env.example → .env and add your key."
    )

# ── Model Settings ─────────────────────────────────────────────────────────
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_DATA_DIR = BASE_DIR / os.getenv("LOCAL_DATA_DIR", "data/local")
DOCS_DIR = BASE_DIR / os.getenv("DOCS_DIR", "data/docs")
VECTOR_STORE_DIR = BASE_DIR / os.getenv("VECTOR_STORE_DIR", "data/vector_store")
SQLITE_DB_PATH = LOCAL_DATA_DIR / "knowledge.db"
RESEARCH_NOTES_PATH = LOCAL_DATA_DIR / "research_notes.txt"

# Ensure directories exist
for d in [LOCAL_DATA_DIR, DOCS_DIR, VECTOR_STORE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── RAG Settings ───────────────────────────────────────────────────────────
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50
TOP_K_RESULTS: int = 4
