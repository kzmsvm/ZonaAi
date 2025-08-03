import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_prompt_handler_missing_provider_config():
    res = client.post("/prompt", json={"prompt": "Hello Zona!", "provider": "openai"})
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
