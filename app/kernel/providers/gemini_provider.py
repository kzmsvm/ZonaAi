import os
from typing import Dict, List

from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Provider that uses Vertex AI's Gemini models."""

    def __init__(
        self,
        project: str | None = None,
        location: str | None = None,
        model: str | None = None,
    ) -> None:
        self.project = project or os.getenv("FIRESTORE_PROJECT_ID")
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._model = None
        if self.project and self.model_name:
            try:  # pragma: no cover - network call not executed in tests
                from google.cloud import aiplatform

                aiplatform.init(project=self.project, location=self.location)
                self._model = aiplatform.GenerativeModel(self.model_name)
            except Exception:  # pragma: no cover - handle missing library
                self._model = None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self._model:
            raise RuntimeError("Gemini model is not configured")

        prompt = messages[-1]["content"]
        response = self._model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text.strip()
        return str(response).strip()
