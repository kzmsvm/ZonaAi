import os
from typing import Dict, List

import openai

from app.storage.memory_store import (
    load_memory,
    save_memory,
    clear_memory as clear_memory_store,
)
from app.utils.license import LicenseManager
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
        self.pending_actions: Dict[str, str] = {}

        # Registered chat providers. Mapped to method names so runtime patches
        # (used in tests) are respected.
        self.providers: Dict[str, str] = {
            "openai": "openai_chat"
        }
        if LicenseManager.validate_license():
            self.providers["gemini"] = "gemini_chat"

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
        if session_id in self.pending_actions:
            confirmation = stripped.lower()
            if confirmation in {"yes", "y"}:
                command = self.pending_actions.pop(session_id)
                return handle_plugin_command(command)
            if confirmation in {"no", "n"}:
                self.pending_actions.pop(session_id)
                return "Cancelled."
            return "Please reply 'yes' or 'no'."

        if stripped == "!clear":
            self.clear_memory(session_id)
            return "Memory cleared."
        if stripped == "!clear_all":
            self.clear_memory()
            return "All memory cleared."
        if stripped.startswith("!"):
            self.pending_actions[session_id] = stripped
            name, *args = stripped[1:].split(maxsplit=1)
            args_str = args[0] if args else ""
            return f"Run plugin `{name}` with args `{args_str}`? (yes/no)"

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

    def gemini_chat(
        self,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        """Placeholder Gemini provider.

        In a real implementation this would call the Google Gemini API. For the
        purposes of testing and development, it simply echoes the prompt with a
        provider-specific prefix.
        """

        content = f"Gemini: {prompt}"
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
