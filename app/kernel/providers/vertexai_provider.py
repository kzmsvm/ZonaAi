import os
from typing import Dict, List

from .base_provider import BaseProvider


class VertexAIProvider(BaseProvider):
    """Provider that uses Google Cloud Vertex AI text generation."""

    def __init__(self, project: str | None = None, location: str | None = None) -> None:
        self.project = project or os.getenv("FIRESTORE_PROJECT_ID")
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self._model = None
        if self.project:
            try:  # pragma: no cover - network calls not executed in tests
                from google.cloud import aiplatform

                aiplatform.init(project=self.project, location=self.location)
                self._model = aiplatform.TextGenerationModel.from_pretrained("gemini-1.5-pro")
            except Exception:  # pragma: no cover - handle missing library
                self._model = None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        if not self._model:
            raise RuntimeError("Vertex AI model is not configured")

        prompt = messages[-1]["content"]
        # Using max_output_tokens similar to OpenAI max_tokens parameter
        response = self._model.predict(prompt, max_output_tokens=100)
        return response.text.strip()
