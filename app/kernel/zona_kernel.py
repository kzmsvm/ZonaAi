import os
import openai


class ZonaKernel:
    """Simple wrapper around OpenAI API with basic text obfuscation."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def obfuscate(self, text: str) -> str:
        """Return a reversed version of the input text."""
        return text[::-1]

    def openai_chat(self, prompt: str) -> str:
        """Send a prompt to the OpenAI ChatCompletion API and return the response."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message["content"].strip()
