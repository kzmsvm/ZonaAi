"""Persistence layer for session memory.

This module handles reading and writing the ``zona_memory.json`` file. To
avoid race conditions when multiple processes or threads access the file, a
simple file locking mechanism is used.
"""

import json
import os
import fcntl
from contextlib import contextmanager
from typing import Dict, List

STORE_PATH = "zona_memory.json"


@contextmanager
def _locked_file(path: str, mode: str):
    """Open ``path`` with ``mode`` and acquire an advisory lock."""
    # Create the directory of the path if it doesn't exist
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, mode, encoding="utf-8") as f:
        lock_type = fcntl.LOCK_EX if "w" in mode or "a" in mode else fcntl.LOCK_SH
        fcntl.flock(f, lock_type)
        try:
            yield f
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def load_memory() -> Dict[str, List[dict]]:
    """Load memory from disk if it exists."""
    if not os.path.exists(STORE_PATH):
        return {}
    with _locked_file(STORE_PATH, "r") as f:
        return json.load(f)


def save_memory(memory: Dict[str, List[dict]]) -> None:
    """Persist memory to disk."""
    with _locked_file(STORE_PATH, "w") as f:
        json.dump(memory, f, indent=2)


def clear_memory() -> None:
    """Remove all persisted memory."""
    # Overwrite the file with an empty JSON object while holding the lock
    save_memory({})
