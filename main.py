"""
main.py
--------
Entry point for the AI Research Assistant.

Run with:
    python main.py

Flow:
  1. Load and chunk documents
  2. Build/load FAISS vector store
  3. Compile LangGraph workflow
  4. Start conversation loop with dual memory (buffer + summary)
"""

import sys
from rich.console import Console

from config.settings import OPENAI_API_KEY
from retrieval.document_loader import load_all_documents
from retrieval.chunker import chunk_documents
from retrieval.vector_store import build_or_load_vector_store
from graph.workflow import build_workflow
from graph.state import ResearchState
from memory.memory_manager import MemoryManager
from utils.helpers import (
    print_banner,
    print_query,
    print_answer,
    print_sources,
    print_separator,
)

console = Console()


def initialize_system():
    """
    Boot sequence: load docs, build vector store, compile graph.
    Returns (compiled_graph, memory_manager).
    """
    console.print("\n[cyan]🔄 Initializing system...[/cyan]")

    # Step 1: Load all documents from data/docs/
    console.print("[dim]  → Loading documents...[/dim]")
    documents = load_all_documents()

    # Step 2: Chunk documents
    console.print("[dim]  → Chunking documents...[/dim]")
    chunks = chunk_documents(documents)

    # Step 3: Build or load FAISS vector store
    console.print("[dim]  → Setting up vector store...[/dim]")
    vector_store = build_or_load_vector_store(chunks)

    # Step 4: Compile LangGraph workflow
    console.print("[dim]  → Compiling LangGraph workflow...[/dim]")
    app = build_workflow(vector_store)

    # Step 5: Initialize memory manager
    memory = MemoryManager()

    console.print("[green]✅ System ready![/green]\n")
    return app, memory


def run_query(app, memory: MemoryManager, query: str) -> str:
    """
    Run a single query through the LangGraph workflow.

    Args:
        app:    Compiled LangGraph workflow
        memory: Memory manager instance
        query:  User's query string

    Returns:
        Final answer string
    """
    # Build the initial state
    state: ResearchState = {
        "query": query,
        "chat_history": memory.format_history_for_prompt(),
        "conversation_summary": memory.get_summary(),
        "plan": None,
        "context": None,
        "final_answer": None,
        "error": None,
        "needs_clarification": False,
    }

    # Run through the graph
    final_state = app.invoke(state)

    answer = final_state.get("final_answer", "No answer generated.")
    sources = (final_state.get("context") or {}).get("sources_used", [])

    # Save to memory
    memory.save_turn(human_input=query, ai_output=answer)

    return answer, sources


def main():
    """Main conversation loop."""
    print_banner()

    # Startup checks
    if not OPENAI_API_KEY:
        console.print("[red]❌ OPENAI_API_KEY not set. Add it to your .env file.[/red]")
        sys.exit(1)

    # Initialize
    try:
        app, memory = initialize_system()
    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        console.print("[yellow]Make sure you have documents in data/docs/ and your .env is configured.[/yellow]")
        sys.exit(1)

    console.print("[dim]Type your research question. Commands: 'quit' to exit, "
                  "'clear' to reset memory, 'history' to see past sessions.[/dim]\n")
    print_separator()

    # ── Main Loop ──────────────────────────────────────────────────────────
    while True:
        try:
            query = input("\n🔍 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]Goodbye! 👋[/cyan]")
            break

        if not query:
            continue

        # ── Special Commands ───────────────────────────────────────────────
        if query.lower() in ("quit", "exit", "q"):
            console.print("[cyan]Goodbye! 👋[/cyan]")
            break

        if query.lower() == "clear":
            memory.clear()
            console.print("[yellow]🧹 Memory cleared.[/yellow]")
            continue

        if query.lower() == "history":
            from mcp_tools.sqlite_mcp import SQLiteMCPServer
            db = SQLiteMCPServer()
            result = db.get_recent_sessions(limit=5)
            if result["success"] and result["sessions"]:
                console.print("\n[bold]📜 Recent Research Sessions:[/bold]")
                for s in result["sessions"]:
                    console.print(f"  [{s['timestamp'][:10]}] {s['query'][:80]}")
            else:
                console.print("[dim]No past sessions found.[/dim]")
            continue

        if query.lower() == "summary":
            summary = memory.get_summary()
            console.print(f"\n[bold]📋 Conversation Summary:[/bold]\n{summary or 'No summary yet.'}")
            continue

        # ── Run the Query ──────────────────────────────────────────────────
        print_separator()
        try:
            console.print("[dim]⏳ Researching...[/dim]")
            answer, sources = run_query(app, memory, query)
            print_answer(answer)
            print_sources(sources)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[dim]Check your API keys and try again.[/dim]")

        print_separator()


if __name__ == "__main__":
    main()
