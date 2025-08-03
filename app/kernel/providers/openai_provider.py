import os
from typing import Dict, List

from openai import OpenAI

from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """Provider that uses OpenAI's Chat Completions API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self.client or not self.model:
            raise RuntimeError("OpenAI client or model is not configured")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
