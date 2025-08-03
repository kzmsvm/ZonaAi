import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_prompt_handler():
    res = client.post("/prompt", json={"prompt": "Hello Zona!"})
    assert res.status_code == 200
    assert "response" in res.json()


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "!anoZ ,olleH"}


def test_static_content():
    res = client.get("/static")
    assert res.status_code == 200
    assert "Zona AI" in res.text
