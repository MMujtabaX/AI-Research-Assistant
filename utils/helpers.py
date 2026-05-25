"""
utils/helpers.py
----------------
Shared utility functions.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_banner():
    """Print the application welcome banner."""
    console.print(Panel.fit(
        "[bold cyan]🔬 AI Research Assistant[/bold cyan]\n"
        "[dim]Multi-Agent System | LangGraph | RAG | MCP | APIs[/dim]",
        border_style="cyan",
    ))


def print_query(query: str):
    """Display the user query."""
    console.print(f"\n[bold yellow]You:[/bold yellow] {query}")


def print_answer(answer: str):
    """Display the final answer in a panel."""
    console.print(Panel(
        answer,
        title="[bold green]🤖 Research Assistant[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


def print_sources(sources: list[str]):
    """Display which sources were used."""
    if sources:
        console.print(f"[dim]📡 Sources consulted: {', '.join(sources)}[/dim]")


def print_separator():
    console.print("[dim]" + "─" * 60 + "[/dim]")


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate a string with ellipsis."""
    return text[:max_len] + "..." if len(text) > max_len else text
