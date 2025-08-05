import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app, kernel

client = TestClient(app)
HEADERS = {"X-API-Key": "test-key"}


def test_prompt_handler_missing_provider_config():
    res = client.post("/prompt", json={"prompt": "Hello Zona!", "provider": "openai"}, headers=HEADERS)
    assert res.status_code == 500
    assert "not configured" in res.json()["detail"]


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "!anoZ ,olleH"}


def test_static_content():
    res = client.get("/static")
    assert res.status_code == 200
    assert "Zona AI" in res.text


def test_delete_memory_endpoint():
    kernel.memory["s123"] = [{"role": "user", "content": "hello"}]
    res = client.delete("/memory/s123")
    assert res.status_code == 200
    assert res.json() == {"status": "deleted"}
    assert "s123" not in kernel.memory
