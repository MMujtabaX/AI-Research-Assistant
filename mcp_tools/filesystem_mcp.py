"""
mcp_tools/filesystem_mcp.py
----------------------------
MCP Server #1 — Filesystem Tool

Simulates an MCP filesystem server that lets agents:
  - Read local notes/files
  - Write new research notes
  - List available files

In production this would call a real MCP server via stdio/SSE transport.
Here we implement the same interface as a local tool wrapper so the
project is fully runnable without a running MCP daemon.
"""

from pathlib import Path
from datetime import datetime
from config.settings import LOCAL_DATA_DIR


class FilesystemMCPServer:
    """
    MCP-style interface for local filesystem operations.

    This mirrors what the official @modelcontextprotocol/server-filesystem
    package exposes as tools. Swap the method bodies for real MCP calls
    once you have the server running.
    """

    def __init__(self, base_dir: Path = LOCAL_DATA_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ── MCP Tool: read_file ────────────────────────────────────────────────
    def read_file(self, filename: str) -> dict:
        """
        Read a file from the local data directory.

        Returns:
            {"success": bool, "content": str, "error": str|None}
        """
        file_path = self.base_dir / filename
        if not file_path.exists():
            return {
                "success": False,
                "content": "",
                "error": f"File not found: {filename}",
            }
        try:
            content = file_path.read_text(encoding="utf-8")
            print(f"[FilesystemMCP] read_file: {filename} ({len(content)} chars)")
            return {"success": True, "content": content, "error": None}
        except Exception as e:
            return {"success": False, "content": "", "error": str(e)}

    # ── MCP Tool: write_file ───────────────────────────────────────────────
    def write_file(self, filename: str, content: str, append: bool = False) -> dict:
        """
        Write or append to a file in the local data directory.

        Returns:
            {"success": bool, "path": str, "error": str|None}
        """
        file_path = self.base_dir / filename
        try:
            mode = "a" if append else "w"
            with open(file_path, mode, encoding="utf-8") as f:
                if append:
                    f.write(f"\n\n--- {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
                f.write(content)
            print(f"[FilesystemMCP] write_file: {filename} (append={append})")
            return {"success": True, "path": str(file_path), "error": None}
        except Exception as e:
            return {"success": False, "path": "", "error": str(e)}

    # ── MCP Tool: list_files ───────────────────────────────────────────────
    def list_files(self, extension: str = "*") -> dict:
        """
        List files in the local data directory.

        Returns:
            {"success": bool, "files": list[str], "error": str|None}
        """
        try:
            pattern = f"*.{extension}" if extension != "*" else "*"
            files = [f.name for f in self.base_dir.glob(pattern) if f.is_file()]
            print(f"[FilesystemMCP] list_files: found {len(files)} file(s)")
            return {"success": True, "files": files, "error": None}
        except Exception as e:
            return {"success": False, "files": [], "error": str(e)}

    # ── MCP Tool: save_research_note ───────────────────────────────────────
    def save_research_note(self, query: str, note: str) -> dict:
        """
        Convenience wrapper — appends a timestamped research note.
        """
        content = f"Query: {query}\n\nNote:\n{note}"
        return self.write_file("research_notes.txt", content, append=True)
