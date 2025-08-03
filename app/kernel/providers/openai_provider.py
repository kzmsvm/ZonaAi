import os
from typing import Dict, List

from openai import OpenAI

from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """Provider that uses OpenAI's Chat Completions API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            return messages[-1]["content"]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message.content.strip()
