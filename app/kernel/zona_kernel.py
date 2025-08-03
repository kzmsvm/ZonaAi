import os
from typing import Dict, List

import openai

from app.storage.memory_store import load_memory, save_memory
from zona.plugin_manager import handle_plugin_command

class ZonaKernel:
    """OpenAI API wrapper with session memory."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.memory: Dict[str, List[dict[str, str]]] = load_memory()

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
        if prompt.startswith("!"):
            return handle_plugin_command(prompt)

        history = self.memory.setdefault(session_id, [])
        history.append({"role": "user", "content": prompt})

        if self.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history,
            )
            content = response.choices[0].message["content"].strip()
        else:
            content = prompt

        history.append({"role": "assistant", "content": content})
        save_memory(self.memory)

        return self.obfuscate(content) if obfuscate_output else content
