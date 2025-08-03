import json
import os
from typing import Dict, List

STORE_PATH = "zona_memory.json"

def load_memory() -> Dict[str, List[dict]]:
    """Load memory from disk if it exists."""
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: Dict[str, List[dict]]) -> None:
    """Persist memory to disk."""
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)
