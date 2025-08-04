"""OpenAI Codex provider for code generation tasks.

This provider exposes a small wrapper around OpenAI's legacy Codex models
which use the Completions API instead of the newer chat interface.  The
implementation mirrors the other provider classes in the project so that it
can be registered with :class:`ZonaKernel` just like the chat based
providers.

The provider is intentionally lightweight – if an API key is not supplied
the class simply raises a ``RuntimeError`` when invoked.  This allows the
rest of the application (and the tests in this kata) to run without access to
the external service while still keeping the integration code in place.
"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from .base_provider import BaseProvider


class CodexProvider(BaseProvider):
    """Provider that uses OpenAI's Codex ``completions`` API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        # ``code-davinci-002`` is the canonical Codex model identifier
        self.model = model or os.getenv("OPENAI_CODE_MODEL", "code-davinci-002")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    # NOTE: ``BaseProvider`` defines ``generate_response`` with a ``messages``
    # parameter (designed for chat based models).  Codex on the other hand
    # expects a single prompt string.  To keep the interface flexible we
    # accept ``prompt`` as ``str`` but still honour the abstract method by
    # providing a compatible signature via ``*args``/``**kwargs``.  The
    # ``prompt`` may be passed either positionally or by keyword.
    def generate_response(self, prompt: Any, **kwargs: Any) -> str:  # type: ignore[override]
        if not self.client or not self.model:
            raise RuntimeError("OpenAI client or model is not configured")

        # If the caller accidentally supplied a list of messages we stitch
        # them together into a plain prompt string.
        if isinstance(prompt, list):
            prompt_text = "\n".join(m.get("content", "") for m in prompt)
        else:
            prompt_text = str(prompt)

        response = self.client.completions.create(
            model=self.model,
            prompt=prompt_text,
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].text.strip()


__all__ = ["CodexProvider"]

