"""
graph/workflow.py
-----------------
LangGraph workflow — the orchestration backbone of the system.

Graph structure:
                    ┌─────────────┐
              ┌────▶│ clarify     │ (if query too vague)
              │     └─────────────┘
  START ──▶ check_query
              │     ┌─────────────┐    ┌────────────┐    ┌─────────────┐
              └────▶│   planner   │──▶ │  retriever │──▶ │ synthesizer │──▶ END
                    └─────────────┘    └────────────┘    └─────────────┘
                           │                  │
                      error branch       error branch
                           │                  │
                           └──────┬───────────┘
                                  ▼
                            ┌───────────┐
                            │   error   │──▶ END
                            └───────────┘
"""

from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import FAISS

from graph.state import ResearchState
from agents.planner_agent import PlannerAgent
from agents.retriever_agent import RetrieverAgent
from agents.synthesizer_agent import SynthesizerAgent


# ── Node Functions ─────────────────────────────────────────────────────────

def check_query_node(state: ResearchState) -> ResearchState:
    """
    Entry node: validates the query before passing it to the planner.
    Routes to 'clarify' if the query is too short or ambiguous.
    """
    query = state.get("query", "").strip()
    print(f"\n{'='*60}")
    print(f"[Graph] check_query_node: '{query[:80]}'")

    if len(query) < 5:
        return {**state, "needs_clarification": True}

    # Check for extremely vague queries
    vague_tokens = {"hi", "hello", "help", "yes", "no", "ok", "okay"}
    if query.lower() in vague_tokens:
        return {**state, "needs_clarification": True}

    return {**state, "needs_clarification": False, "error": None}


def clarify_node(state: ResearchState) -> ResearchState:
    """Handles queries that are too vague — returns a clarification request."""
    print("[Graph] clarify_node: Query needs clarification")
    return {
        **state,
        "final_answer": (
            "Your query seems quite brief. Could you please provide more detail?\n"
            "For example:\n"
            "• What specific topic or field are you researching?\n"
            "• What aspect are you most interested in?\n"
            "• Are you looking for recent news, academic info, or general knowledge?"
        ),
    }


def planner_node(state: ResearchState) -> ResearchState:
    """Runs the Planner Agent to create a research plan."""
    print("[Graph] planner_node: Running PlannerAgent...")
    try:
        agent = PlannerAgent()
        plan = agent.plan(
            query=state["query"],
            chat_history=state.get("chat_history", ""),
            conversation_summary=state.get("conversation_summary", ""),
        )
        return {**state, "plan": plan, "error": None}
    except Exception as e:
        print(f"[Graph] planner_node ERROR: {e}")
        return {**state, "error": f"Planner failed: {str(e)}"}


def retriever_node(state: ResearchState, vector_store: FAISS) -> ResearchState:
    """Runs the Retriever Agent to gather context from all sources."""
    print("[Graph] retriever_node: Running RetrieverAgent...")
    try:
        agent = RetrieverAgent(vector_store=vector_store)
        context = agent.retrieve(
            query=state["query"],
            plan=state.get("plan", {}),
        )
        return {**state, "context": context, "error": None}
    except Exception as e:
        print(f"[Graph] retriever_node ERROR: {e}")
        return {**state, "error": f"Retriever failed: {str(e)}"}


def synthesizer_node(state: ResearchState) -> ResearchState:
    """Runs the Synthesizer Agent to produce the final answer."""
    print("[Graph] synthesizer_node: Running SynthesizerAgent...")
    try:
        agent = SynthesizerAgent()
        answer = agent.synthesize(
            query=state["query"],
            plan=state.get("plan", {}),
            context=state.get("context", {}),
            chat_history=state.get("chat_history", ""),
        )
        return {**state, "final_answer": answer, "error": None}
    except Exception as e:
        print(f"[Graph] synthesizer_node ERROR: {e}")
        return {**state, "error": f"Synthesizer failed: {str(e)}"}


def error_node(state: ResearchState) -> ResearchState:
    """Graceful error handler — surfaces the error as the final answer."""
    print(f"[Graph] error_node: {state.get('error')}")
    return {
        **state,
        "final_answer": (
            f"⚠️ I encountered an error while researching your query.\n\n"
            f"Error: {state.get('error', 'Unknown error')}\n\n"
            "Please check your API keys in the .env file and try again."
        ),
    }


# ── Conditional Routing Functions ──────────────────────────────────────────

def route_after_check(state: ResearchState) -> str:
    """After check_query: go to clarify or planner."""
    if state.get("needs_clarification"):
        return "clarify"
    return "planner"


def route_after_planner(state: ResearchState) -> str:
    """After planner: go to retriever or error handler."""
    if state.get("error"):
        return "error"
    return "retriever"


def route_after_retriever(state: ResearchState) -> str:
    """After retriever: go to synthesizer or error handler."""
    if state.get("error"):
        return "error"
    return "synthesizer"


def route_after_synthesizer(state: ResearchState) -> str:
    """After synthesizer: end or error handler."""
    if state.get("error"):
        return "error"
    return END


# ── Graph Builder ──────────────────────────────────────────────────────────

def build_workflow(vector_store: FAISS) -> "CompiledGraph":
    """
    Assembles and compiles the LangGraph workflow.

    Args:
        vector_store: Pre-loaded FAISS vector store

    Returns:
        A compiled LangGraph app ready to invoke
    """
    graph = StateGraph(ResearchState)

    # ── Register Nodes ─────────────────────────────────────────────────────
    graph.add_node("check_query", check_query_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("planner", planner_node)
    # Wrap retriever_node to inject vector_store (LangGraph doesn't pass extra args)
    graph.add_node(
        "retriever",
        lambda state: retriever_node(state, vector_store),
    )
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("error", error_node)

    # ── Set Entry Point ────────────────────────────────────────────────────
    graph.set_entry_point("check_query")

    # ── Add Conditional Edges ──────────────────────────────────────────────
    graph.add_conditional_edges(
        "check_query",
        route_after_check,
        {"clarify": "clarify", "planner": "planner"},
    )
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"retriever": "retriever", "error": "error"},
    )
    graph.add_conditional_edges(
        "retriever",
        route_after_retriever,
        {"synthesizer": "synthesizer", "error": "error"},
    )
    graph.add_conditional_edges(
        "synthesizer",
        route_after_synthesizer,
        {END: END, "error": "error"},
    )

    # ── Terminal Nodes ─────────────────────────────────────────────────────
    graph.add_edge("clarify", END)
    graph.add_edge("error", END)

    return graph.compile()
