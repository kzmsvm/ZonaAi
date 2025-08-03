import os
from typing import Dict, List, Protocol

from app.storage.memory_store import (
    load_memory,
    save_memory,
    clear_memory as clear_memory_store,
)
from zona.plugin_manager import handle_plugin_command
from app.providers.openai_provider import OpenAIProvider


class ChatProvider(Protocol):
    """Protocol for chat providers."""

    def chat(self, messages: List[dict[str, str]]) -> str:
        """Return the assistant's reply for the given message history."""
        ...

class ZonaKernel:
    """OpenAI API wrapper with session memory."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        max_messages: int | None = 20,
        max_total_length: int | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.memory: Dict[str, List[dict[str, str]]] = load_memory()
        self.max_messages = max_messages
        self.max_total_length = max_total_length

    def obfuscate(self, text: str) -> str:
        """Return a reversed version of the input text."""
        return text[::-1]

    def chat(
        self,
        provider: ChatProvider,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        """Send a prompt to a provider with session memory."""
        stripped = prompt.strip()
        if stripped == "!clear":
            self.clear_memory(session_id)
            return "Memory cleared."
        if stripped == "!clear_all":
            self.clear_memory()
            return "All memory cleared."
        if stripped.startswith("!"):
            return handle_plugin_command(stripped)

        history = self.memory.setdefault(session_id, [])
        history.append({"role": "user", "content": prompt})
        self._trim_history(history)

        content = provider.chat(history)

        history.append({"role": "assistant", "content": content})
        self._trim_history(history)
        save_memory(self.memory)

        return self.obfuscate(content) if obfuscate_output else content

    def openai_chat(
        self,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        """Backward-compatible OpenAI chat helper."""
        provider = OpenAIProvider(self.api_key)
        return self.chat(
            provider,
            prompt,
            session_id=session_id,
            obfuscate_output=obfuscate_output,
        )

    # ------------------------------------------------------------------
    def _trim_history(self, history: List[dict[str, str]]) -> None:
        """Enforce limits on a session's history."""
        if self.max_messages is not None and len(history) > self.max_messages:
            del history[:-self.max_messages]
        if self.max_total_length is not None:
            total = sum(len(item["content"]) for item in history)
            while history and total > self.max_total_length:
                removed = history.pop(0)
                total -= len(removed["content"])

    def clear_memory(self, session_id: str | None = None) -> None:
        """Clear memory for a session or all sessions."""
        if session_id is None:
            self.memory.clear()
            clear_memory_store()
        else:
            self.memory.pop(session_id, None)
            save_memory(self.memory)
