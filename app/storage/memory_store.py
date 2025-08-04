"""Persistence layer for session memory backed by Firestore or a database.

This module stores chat session history in Google Cloud Firestore. When
Firestore is not configured (e.g. during local development or in test
environments), it can optionally persist data in a SQL database (SQLite or
Postgres) or fall back to an in-memory cache so the rest of the application can
operate without external dependencies.
"""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency
    from google.cloud import firestore  # type: ignore
except Exception:  # pragma: no cover - library missing or misconfigured
    firestore = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import psycopg2
except Exception:  # pragma: no cover - library missing or misconfigured
    psycopg2 = None


class MemoryStore:
    """Store chat session memory in Firestore or a SQL database."""

    def __init__(
        self,
        *,
        project_id: Optional[str] = None,
        collection: str = "zona",
        document: str = "memory",
        database_url: Optional[str] = None,
    ) -> None:
        self.collection = collection
        self.document = document
        self._memory: Dict[str, List[dict]] = {}

        self._client = None
        self._db_conn = None

        project = project_id or os.getenv("FIRESTORE_PROJECT_ID")
        use_firestore = os.getenv("USE_FIRESTORE", "false").lower() in {"1", "true", "yes"}
        if use_firestore and firestore is not None and project:
            try:  # pragma: no cover - requires valid credentials
                self._client = firestore.Client(project=project)
            except Exception:
                self._client = None

        if self._client is None:
            db_url = database_url or os.getenv("DATABASE_URL")
            if db_url:
                self._init_db(db_url)

    # ------------------------------------------------------------------
    # Database helpers
    def _init_db(self, db_url: str) -> None:  # pragma: no cover - simple helper
        parsed = urlparse(db_url)
        if parsed.scheme in {"sqlite", ""}:
            path = parsed.path or parsed.netloc
            self._db_conn = sqlite3.connect(path or ":memory:")
        elif parsed.scheme in {"postgres", "postgresql"} and psycopg2 is not None:
            self._db_conn = psycopg2.connect(db_url)  # type: ignore[arg-type]
        else:
            self._db_conn = None
        if self._db_conn is not None:
            cursor = self._db_conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, data TEXT)"
            )
            self._db_conn.commit()

    # ------------------------------------------------------------------
    # Helper methods
    def _doc_ref(self):  # pragma: no cover - simple helper
        if self._client is None:
            return None
        return self._client.collection(self.collection).document(self.document)

    # ------------------------------------------------------------------
    # Public API
    def load_memory(self) -> Dict[str, List[dict]]:
        """Load memory from Firestore, a database, or return cached value."""
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

        if self._db_conn is not None:
            try:
                cursor = self._db_conn.cursor()
                cursor.execute("SELECT data FROM memory WHERE id=1")
                row = cursor.fetchone()
                if row and row[0]:
                    self._memory = json.loads(row[0])
            except Exception:
                pass
            return dict(self._memory)

        return dict(self._memory)

    def save_memory(self, memory: Dict[str, List[dict]]) -> None:
        """Persist memory to Firestore/DB and update the cache."""
        self._memory = memory
        doc_ref = self._doc_ref()
        if doc_ref is not None:
            try:
                doc_ref.set(memory)
            except Exception:
                pass
        elif self._db_conn is not None:
            try:
                cursor = self._db_conn.cursor()
                cursor.execute(
                    "INSERT INTO memory(id, data) VALUES(1, ?)"
                    " ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                    (json.dumps(memory),),
                )
                self._db_conn.commit()
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
        elif self._db_conn is not None:
            try:
                cursor = self._db_conn.cursor()
                cursor.execute("DELETE FROM memory")
                self._db_conn.commit()
            except Exception:
                pass

    def close(self) -> None:
        """Close any open database connection."""
        if self._db_conn is not None:
            try:
                self._db_conn.close()
            except Exception:
                pass
            finally:
                self._db_conn = None

    def __del__(self):  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:
            pass


__all__ = ["MemoryStore"]

