import os
from typing import Dict, List

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - library may be missing during tests
    genai = None

from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Provider that uses Google's Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-pro")
        if self.api_key and genai is not None and self.model_name:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self.model:
            raise RuntimeError("Gemini model is not configured")

        history: List[Dict[str, str]] = []
        for m in messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = self.model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        return response.text.strip()
