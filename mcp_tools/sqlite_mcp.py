"""
mcp_tools/sqlite_mcp.py
------------------------
MCP Server #2 — SQLite Database Tool

Simulates an MCP SQLite server that lets agents:
  - Store and query research sessions
  - Log sources used per query
  - Retrieve conversation history from DB

Mirrors what @modelcontextprotocol/server-sqlite would expose as tools.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config.settings import SQLITE_DB_PATH


class SQLiteMCPServer:
    """
    MCP-style interface for a local SQLite knowledge database.

    Tables:
      - research_sessions: stores each query + final answer
      - sources_used: tracks which APIs/docs contributed to each answer
    """

    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_sessions (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query     TEXT NOT NULL,
                    answer    TEXT,
                    sources   TEXT  -- JSON array of source names
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sources_used (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id  INTEGER REFERENCES research_sessions(id),
                    source_type TEXT,   -- 'rag', 'news_api', 'open_library', 'filesystem'
                    source_name TEXT,
                    snippet     TEXT    -- short excerpt
                )
            """)
            conn.commit()
        print(f"[SQLiteMCP] Database ready: {self.db_path}")

    # ── MCP Tool: save_session ─────────────────────────────────────────────
    def save_session(self, query: str, answer: str, sources: list[str]) -> dict:
        """
        Save a completed research session to the DB.

        Returns:
            {"success": bool, "session_id": int, "error": str|None}
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO research_sessions (timestamp, query, answer, sources) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        datetime.now().isoformat(),
                        query,
                        answer,
                        json.dumps(sources),
                    ),
                )
                session_id = cursor.lastrowid
                conn.commit()
            print(f"[SQLiteMCP] Saved session #{session_id} for query: '{query[:50]}'")
            return {"success": True, "session_id": session_id, "error": None}
        except Exception as e:
            return {"success": False, "session_id": -1, "error": str(e)}

    # ── MCP Tool: log_source ───────────────────────────────────────────────
    def log_source(
        self,
        session_id: int,
        source_type: str,
        source_name: str,
        snippet: str = "",
    ) -> dict:
        """Log an individual source used in a research session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO sources_used (session_id, source_type, source_name, snippet) "
                    "VALUES (?, ?, ?, ?)",
                    (session_id, source_type, source_name, snippet[:300]),
                )
                conn.commit()
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── MCP Tool: get_recent_sessions ─────────────────────────────────────
    def get_recent_sessions(self, limit: int = 5) -> dict:
        """
        Retrieve the most recent research sessions.

        Returns:
            {"success": bool, "sessions": list[dict], "error": str|None}
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM research_sessions ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            sessions = [dict(row) for row in rows]
            print(f"[SQLiteMCP] Retrieved {len(sessions)} recent session(s)")
            return {"success": True, "sessions": sessions, "error": None}
        except Exception as e:
            return {"success": False, "sessions": [], "error": str(e)}

    # ── MCP Tool: search_sessions ──────────────────────────────────────────
    def search_sessions(self, keyword: str) -> dict:
        """Search past sessions by keyword in query or answer."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM research_sessions "
                    "WHERE query LIKE ? OR answer LIKE ? "
                    "ORDER BY id DESC LIMIT 10",
                    (f"%{keyword}%", f"%{keyword}%"),
                ).fetchall()
            sessions = [dict(row) for row in rows]
            return {"success": True, "sessions": sessions, "error": None}
        except Exception as e:
            return {"success": False, "sessions": [], "error": str(e)}
