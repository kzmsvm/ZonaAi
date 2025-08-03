import os
import sys
from pathlib import Path

# Ensure project root is in sys.path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.storage.memory_store import MemoryStore


def test_sqlite_persistence(tmp_path, monkeypatch):
    db_file = tmp_path / "mem.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    store = MemoryStore()
    data = {"s1": [{"role": "user", "content": "hi"}]}
    store.save_memory(data)
    loaded = store.load_memory()
    assert loaded == data
    store.clear_memory()
    assert store.load_memory() == {}
