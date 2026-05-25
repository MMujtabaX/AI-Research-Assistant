"""
graph/state.py
--------------
Defines the LangGraph state that flows through the entire workflow.
Every node reads from and writes to this typed dict.
"""

from typing import TypedDict, Optional


class ResearchState(TypedDict):
    """
    The shared state that passes through the LangGraph workflow.
    Each agent node reads what it needs and adds its outputs.
    """

    # ── Input ──────────────────────────────────────────────────────────────
    query: str                      # The user's raw question

    # ── Memory / History ──────────────────────────────────────────────────
    chat_history: str               # Formatted buffer memory (last N turns)
    conversation_summary: str       # Compressed summary memory

    # ── Planner Output ────────────────────────────────────────────────────
    plan: Optional[dict]            # Research plan from PlannerAgent

    # ── Retriever Output ──────────────────────────────────────────────────
    context: Optional[dict]         # All gathered context from RetrieverAgent

    # ── Synthesizer Output ────────────────────────────────────────────────
    final_answer: Optional[str]     # The final answer from SynthesizerAgent

    # ── Routing ───────────────────────────────────────────────────────────
    error: Optional[str]            # Set if any node fails — routes to error handler
    needs_clarification: bool       # True if query is too vague
