"""
agents/synthesizer_agent.py
----------------------------
Agent #3 — Synthesizer Agent

Responsibility:
  Takes all retrieved context (RAG results, news, books, local notes)
  and the original query, then writes a comprehensive, cited final answer.

  Also handles:
    - Saving the answer to SQLite MCP
    - Appending a note to the filesystem MCP
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from mcp_tools.sqlite_mcp import SQLiteMCPServer
from mcp_tools.filesystem_mcp import FilesystemMCPServer
from config.settings import OPENAI_MODEL, OPENAI_API_KEY


SYNTHESIZER_PROMPT = PromptTemplate(
    input_variables=[
        "query",
        "chat_history",
        "rag_context",
        "news_context",
        "books_context",
        "local_notes",
        "sub_questions",
    ],
    template="""You are a Research Synthesizer Agent. Your job is to write a thorough,
well-organized answer to the user's research question by combining information from
multiple sources.

=== RECENT CONVERSATION ===
{chat_history}

=== USER QUERY ===
{query}

=== SUB-QUESTIONS TO ADDRESS ===
{sub_questions}

=== CONTEXT FROM LOCAL DOCUMENTS (RAG) ===
{rag_context}

=== CONTEXT FROM RECENT NEWS ===
{news_context}

=== CONTEXT FROM BOOKS ===
{books_context}

=== YOUR SAVED RESEARCH NOTES ===
{local_notes}

=== INSTRUCTIONS ===
Write a comprehensive, well-structured answer that:
1. Directly answers the main query
2. Addresses each sub-question
3. Integrates information from multiple sources where available
4. Clearly attributes information to its source (e.g. "[News]", "[Book]", "[Local Docs]")
5. Is organized with clear headings if the answer is long
6. Ends with a "Key Takeaways" section with 3-5 bullet points

If some sources had no relevant information, still write the best answer you can
from the sources that did.

=== YOUR ANSWER ==="""
)


class SynthesizerAgent:
    """
    Synthesizer Agent: Combines all retrieved information into a final answer.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3,
        )
        self.chain = SYNTHESIZER_PROMPT | self.llm | StrOutputParser()
        self.sqlite_mcp = SQLiteMCPServer()
        self.fs_mcp = FilesystemMCPServer()

    def synthesize(
        self,
        query: str,
        plan: dict,
        context: dict,
        chat_history: str = "",
    ) -> str:
        """
        Generate the final answer from all gathered context.

        Args:
            query:        Original user query
            plan:         Planner's research plan
            context:      Retriever's gathered context
            chat_history: Formatted recent conversation

        Returns:
            Final answer string
        """
        print(f"\n[SynthesizerAgent] Synthesizing answer...")

        # Format RAG results
        rag_text = self._format_rag(context.get("rag_results", []))

        # Build sub-questions string
        sub_q = plan.get("sub_questions", [query])
        sub_questions_str = "\n".join(f"- {q}" for q in sub_q)

        answer = self.chain.invoke({
            "query": query,
            "chat_history": chat_history or "No prior conversation.",
            "rag_context": rag_text,
            "news_context": context.get("news_text") or "No news data retrieved.",
            "books_context": context.get("books_text") or "No book data retrieved.",
            "local_notes": context.get("local_notes") or "No local notes found.",
            "sub_questions": sub_questions_str,
        })

        # ── Persist via MCP servers ────────────────────────────────────────
        self._persist(query, answer, context.get("sources_used", []))

        print(f"[SynthesizerAgent] Answer generated ({len(answer)} chars)")
        return answer

    def _format_rag(self, rag_docs: list) -> str:
        if not rag_docs:
            return "No relevant passages found in local documents."
        lines = ["Relevant passages from local documents:\n"]
        for i, doc in enumerate(rag_docs, 1):
            source = doc.metadata.get("source", "unknown")
            lines.append(f"{i}. [Source: {source}]\n{doc.page_content}\n")
        return "\n".join(lines)

    def _persist(self, query: str, answer: str, sources: list[str]) -> None:
        """Save session to SQLite and append note to filesystem."""
        try:
            # Save to SQLite via MCP
            result = self.sqlite_mcp.save_session(
                query=query,
                answer=answer[:1000],  # truncate for DB
                sources=sources,
            )
            if result["success"]:
                session_id = result["session_id"]
                # Log each source
                for src in sources:
                    self.sqlite_mcp.log_source(
                        session_id=session_id,
                        source_type=src,
                        source_name=src,
                    )

            # Append a short note to filesystem via MCP
            short_answer = answer[:300] + "..." if len(answer) > 300 else answer
            self.fs_mcp.save_research_note(query=query, note=short_answer)

        except Exception as e:
            print(f"[SynthesizerAgent] Persistence error (non-fatal): {e}")
