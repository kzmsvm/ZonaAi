import os
from typing import Dict, List

import openai

from app.storage.memory_store import (
    load_memory,
    save_memory,
    clear_memory as clear_memory_store,
)
from zona.plugin_manager import handle_plugin_command

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
        if self.api_key:
            openai.api_key = self.api_key
        self.memory: Dict[str, List[dict[str, str]]] = load_memory()
        self.max_messages = max_messages
        self.max_total_length = max_total_length

    def obfuscate(self, text: str) -> str:
        """Return a reversed version of the input text."""
        return text[::-1]

    def openai_chat(
        self,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        """Send a prompt to the OpenAI ChatCompletion API with session memory."""
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

        if self.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history,
            )
            content = response.choices[0].message["content"].strip()
        else:
            content = prompt

        history.append({"role": "assistant", "content": content})
        self._trim_history(history)
        save_memory(self.memory)

        return self.obfuscate(content) if obfuscate_output else content

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
