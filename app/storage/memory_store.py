"""Persistence layer for session memory backed by Firestore.

This module stores chat session history in Google Cloud Firestore. When
Firestore is not configured (e.g. during local development or in test
environments), it falls back to an in-memory cache so the rest of the
application can operate without external dependencies.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

try:  # pragma: no cover - optional dependency
    from google.cloud import firestore  # type: ignore
except Exception:  # pragma: no cover - library missing or misconfigured
    firestore = None  # type: ignore


class MemoryStore:
    """Store chat session memory in Firestore."""

    def __init__(
        self,
        *,
        project_id: Optional[str] = None,
        collection: str = "zona",
        document: str = "memory",
    ) -> None:
        self.collection = collection
        self.document = document
        self._memory: Dict[str, List[dict]] = {}

        self._client = None
        project = project_id or os.getenv("FIRESTORE_PROJECT_ID")
        if firestore is not None and project:
            try:  # pragma: no cover - requires valid credentials
                self._client = firestore.Client(project=project)
            except Exception:
                self._client = None

    # ------------------------------------------------------------------
    # Helper methods
    def _doc_ref(self):  # pragma: no cover - simple helper
        if self._client is None:
            return None
        return self._client.collection(self.collection).document(self.document)

    # ------------------------------------------------------------------
    # Public API
    def load_memory(self) -> Dict[str, List[dict]]:
        """Load memory from Firestore or return cached value."""
        doc_ref = self._doc_ref()
        if doc_ref is not None:
            try:
                snapshot = doc_ref.get()
                if snapshot.exists:
                    data = snapshot.to_dict() or {}
                    self._memory = data
                    return data
            except Exception:
                pass
        return dict(self._memory)

    def save_memory(self, memory: Dict[str, List[dict]]) -> None:
        """Persist memory to Firestore and update the cache."""
        self._memory = memory
        doc_ref = self._doc_ref()
        if doc_ref is not None:
            try:
                doc_ref.set(memory)
            except Exception:
                pass

    def clear_memory(self) -> None:
        """Remove all persisted memory."""
        self._memory = {}
        doc_ref = self._doc_ref()
        if doc_ref is not None:
            try:
                doc_ref.delete()
            except Exception:
                pass


__all__ = ["MemoryStore"]

