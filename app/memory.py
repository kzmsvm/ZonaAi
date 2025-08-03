from __future__ import annotations

from typing import List, Dict


class MemoryStore:
    """Simple in-memory store for prompt/response history."""

    def __init__(self) -> None:
        self._history: List[Dict[str, str]] = []

    def add_entry(self, user_prompt: str, response: str) -> None:
        """Record a prompt/response pair."""
        self._history.append({"prompt": user_prompt, "response": response})

    def get_history(self) -> List[Dict[str, str]]:
        """Return the stored conversation history."""
        return list(self._history)
