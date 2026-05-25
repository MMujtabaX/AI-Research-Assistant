"""
memory/memory_manager.py
------------------------
Implements two memory strategies:
  1. ConversationBufferMemory  — keeps the full raw conversation history
  2. ConversationSummaryMemory — keeps a running compressed summary

The MemoryManager wraps both and exposes a unified interface.
"""

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_MODEL, OPENAI_API_KEY


class MemoryManager:
    """
    Manages two parallel memory objects so agents can choose which
    context view they need:
      - buffer_memory  → exact recent turns (good for short sessions)
      - summary_memory → compressed history (good for long sessions)
    """

    def __init__(self):
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0,
        )

        # 1️⃣ Buffer Memory — stores every message verbatim
        self.buffer_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,  # returns BaseMessage objects
        )

        # 2️⃣ Summary Memory — compresses old turns into a running summary
        self.summary_memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="summary_history",
            return_messages=False,  # returns plain text summary
        )

    def save_turn(self, human_input: str, ai_output: str) -> None:
        """Save a completed conversation turn to both memory objects."""
        self.buffer_memory.save_context(
            {"input": human_input},
            {"output": ai_output},
        )
        self.summary_memory.save_context(
            {"input": human_input},
            {"output": ai_output},
        )

    def get_buffer_history(self) -> list:
        """Return raw message list from buffer memory."""
        return self.buffer_memory.load_memory_variables({}).get("chat_history", [])

    def get_summary(self) -> str:
        """Return compressed text summary of the conversation so far."""
        return self.summary_memory.load_memory_variables({}).get("summary_history", "")

    def clear(self) -> None:
        """Reset both memory stores (e.g. on new session)."""
        self.buffer_memory.clear()
        self.summary_memory.clear()

    def format_history_for_prompt(self) -> str:
        """
        Returns a human-readable string of recent turns for injection
        into agent prompts.
        """
        messages = self.get_buffer_history()
        if not messages:
            return "No prior conversation."
        lines = []
        for msg in messages[-6:]:  # last 3 turns (human + AI each)
            role = "User" if msg.type == "human" else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)
