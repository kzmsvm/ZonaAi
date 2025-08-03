from fastapi.testclient import TestClient
from app.main import app, kernel

client = TestClient(app)


def test_prompt_handler_returns_response(monkeypatch):
    """Ensure /prompt uses kernel for responses."""

    monkeypatch.setattr(
        kernel,
        "openai_chat",
        lambda prompt, session_id="default", obfuscate_output=False: "mocked",
    )
    response = client.post("/prompt", json={"prompt": "hi"})
    assert response.status_code == 200
    assert response.json() == {"response": "mocked"}
