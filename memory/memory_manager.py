from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_MODEL, OPENAI_API_KEY

class MemoryManager:
    def __init__(self):
        self.history = ChatMessageHistory()
        self.llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)
        self._summary = ""

    def save_turn(self, human_input: str, ai_output: str) -> None:
        self.history.add_user_message(human_input)
        self.history.add_ai_message(ai_output)
        self._update_summary(human_input, ai_output)

    def _update_summary(self, human_input: str, ai_output: str) -> None:
        try:
            prompt = (
                f"Current summary: {self._summary}\n\n"
                f"New turn:\nUser: {human_input}\nAssistant: {ai_output[:300]}\n\n"
                f"Update the summary in 2-3 sentences:"
            )
            result = self.llm.invoke(prompt)
            self._summary = result.content
        except Exception:
            pass

    def get_buffer_history(self) -> list:
        return self.history.messages

    def get_summary(self) -> str:
        return self._summary

    def clear(self) -> None:
        self.history.clear()
        self._summary = ""

    def format_history_for_prompt(self) -> str:
        messages = self.history.messages[-6:]
        if not messages:
            return "No prior conversation."
        lines = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)
