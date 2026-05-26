"""
agents/planner_agent.py
------------------------
Agent #1 — Planner Agent

Responsibility:
  Receives the raw user query and breaks it into a structured research plan.
  Determines:
    - Whether to use RAG (local docs)
    - Whether to fetch news
    - Whether to search books
    - The key search terms to use for each source

Output: A structured plan dict consumed by the Retriever Agent.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

from config.settings import OPENAI_MODEL, OPENAI_API_KEY


PLANNER_PROMPT = PromptTemplate(
    input_variables=["query", "chat_history", "conversation_summary"],
    template="""You are a Research Planner Agent. Your job is to analyze a user's research query
and produce a structured JSON plan for other agents to follow.

=== CONVERSATION SUMMARY ===
{conversation_summary}

=== RECENT CHAT HISTORY ===
{chat_history}

=== USER QUERY ===
{query}

=== YOUR TASK ===
Analyze this query and output a JSON plan (and ONLY JSON, no extra text) with this structure:
{{
  "search_terms": ["term1", "term2"],
  "use_local_docs": true or false,
  "use_news_api": true or false,
  "use_books_api": true or false,
  "sub_questions": ["sub-question 1", "sub-question 2"],
  "reasoning": "Brief explanation of why you chose these sources"
}}

Rules:
- use_local_docs = true if the query involves knowledge that may be in uploaded research docs
- use_news_api = true if the query involves recent events, news, or current developments
- use_books_api = true if the query involves academic topics, classic knowledge, or books
- Always provide 2-3 focused search_terms
- Break the query into 1-3 sub_questions that can be answered independently

JSON plan:"""
)


class PlannerAgent:
    """
    Planner Agent: Decomposes the user query into a research plan.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0,
        )
        self.chain = PLANNER_PROMPT | self.llm | StrOutputParser()

    def plan(
        self,
        query: str,
        chat_history: str = "",
        conversation_summary: str = "",
    ) -> dict:
        """
        Generate a research plan for the given query.

        Returns:
            dict with keys: search_terms, use_local_docs, use_news_api,
                           use_books_api, sub_questions, reasoning
        """
        print(f"\n[PlannerAgent] Planning for query: '{query[:80]}'")

        raw = self.chain.invoke({
            "query": query,
            "chat_history": chat_history or "No prior conversation.",
            "conversation_summary": conversation_summary or "No summary yet.",
        })

        # Parse the JSON response
        plan = self._parse_json(raw)

        print(f"[PlannerAgent] Plan: sources={self._active_sources(plan)}, "
              f"terms={plan.get('search_terms', [])}")
        return plan

    def _parse_json(self, raw: str) -> dict:
        """Safely parse JSON from the LLM output."""
        # Strip markdown code fences if present
        raw = re.sub(r"```json|```", "", raw).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"[PlannerAgent] ⚠️  JSON parse failed, using defaults. Raw: {raw[:200]}")
            return {
                "search_terms": ["general research"],
                "use_local_docs": True,
                "use_news_api": True,
                "use_books_api": True,
                "sub_questions": [raw[:100]],
                "reasoning": "Fallback plan due to parse error.",
            }

    def _active_sources(self, plan: dict) -> list[str]:
        sources = []
        if plan.get("use_local_docs"):
            sources.append("local_docs")
        if plan.get("use_news_api"):
            sources.append("news_api")
        if plan.get("use_books_api"):
            sources.append("books_api")
        return sources
