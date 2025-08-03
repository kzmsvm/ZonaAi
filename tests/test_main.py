from fastapi.testclient import TestClient
from app.main import app, kernel


client = TestClient(app)


def test_prompt_handler_returns_response(monkeypatch):
    """Basic endpoint smoke test with a mocked kernel."""

    monkeypatch.setattr(
        kernel,
        "openai_chat",
        lambda prompt, session_id="default", obfuscate_output=False: "mocked",
    )
    res = client.post("/prompt", json={"prompt": "Hello Zona!"})
    assert res.status_code == 200
    assert res.json() == {"response": "mocked"}


def test_prompt_handler_obfuscates_output():
    res = client.post(
        "/prompt", json={"prompt": "Hello", "obfuscate_output": True}
    )
    assert res.status_code == 200
    assert res.json() == {"response": "olleH"}
