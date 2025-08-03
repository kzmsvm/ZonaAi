import os
import openai


class OpenAIProvider:
    """Simple wrapper around OpenAI's ChatCompletion API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def chat(self, messages: list[dict[str, str]]) -> str:
        if self.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            return response.choices[0].message["content"].strip()
        # Fallback echo for offline development
        return messages[-1]["content"]
