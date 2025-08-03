import os
from typing import Dict, List

import openai

from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """Provider that uses OpenAI's ChatCompletion API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            return messages[-1]["content"]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message["content"].strip()
