from __future__ import annotations

from typing import Any, Dict, List

try:
    from transformers import pipeline
except Exception:  # pragma: no cover - optional dependency
    pipeline = None  # type: ignore[assignment]

from .base_provider import BaseProvider


class CodeLlamaProvider(BaseProvider):
    """Provider that uses a local Code Llama model via ``transformers``."""

    def __init__(self, model: str | None = None, **pipeline_kwargs: Any) -> None:
        if pipeline is None:
            raise RuntimeError("transformers library is not installed")
        model_name = model or "codellama/CodeLlama-7b-hf"
        self.pipeline = pipeline(
            "text-generation", model=model_name, **pipeline_kwargs
        )

    def generate_response(self, messages: List[Dict[str, str]] | str, **kwargs: Any) -> str:  # type: ignore[override]
        if isinstance(messages, list):
            prompt = "\n".join(m.get("content", "") for m in messages)
        else:
            prompt = str(messages)
        result = self.pipeline(prompt, max_length=kwargs.get("max_tokens", 1000))
        return result[0]["generated_text"]
