import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app, kernel

client = TestClient(app)


def test_prompt_handler_returns_response():
    # kernel.chat fonksiyonunu mockluyoruz
    kernel.chat = lambda provider, prompt, session_id="default", obfuscate_output=False: "mocked"

    # API isteği gönder
    response = client.post("/prompt", json={"prompt": "hi", "provider": "openai"})

    # Doğrulama
    assert response.status_code == 200
    assert response.json() == {"response": "mocked"}
