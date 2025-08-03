from __future__ import annotations

def log_interaction(session_id: str, prompt: str, response: str) -> None:
    print(f"[{session_id}] >> {prompt}")
    print(f"[{session_id}] << {response}")
