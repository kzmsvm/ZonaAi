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
