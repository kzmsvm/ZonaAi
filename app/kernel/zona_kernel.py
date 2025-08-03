import os
from typing import Dict, List
import openai


class ZonaKernel:
    """OpenAI API wrapper with session memory."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.memory: Dict[str, List[dict[str, str]]] = {}

    def obfuscate(self, text: str) -> str:
        """Return a reversed version of the input text."""
        return text[::-1]

    def openai_chat(self, prompt: str, session_id: str = "default") -> str:
        """Send a prompt to the OpenAI ChatCompletion API with session memory."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        history = self.memory.setdefault(session_id, [])
        history.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history,
        )

        content = response.choices[0].message["content"].strip()
        history.append({"role": "assistant", "content": content})

        return self.obfuscate(content)  # ya da `return content` (prod için)
