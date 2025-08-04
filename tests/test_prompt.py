import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app, kernel

client = TestClient(app)


def test_prompt_handler_returns_response():
    original_chat = kernel.chat
    kernel.chat = lambda provider, prompt, session_id="default", obfuscate_output=False: "mocked"

    response = client.post("/prompt", json={"prompt": "hi", "provider": "openai"})

    assert response.status_code == 200
    assert response.json() == {"response": "mocked"}
    kernel.chat = original_chat


def test_vertexai_prompt_handler_requires_license_and_returns_response():
    os.environ["LICENSE_KEY"] = "valid"
    original_chat = kernel.chat
    kernel.chat = lambda provider, prompt, session_id="default", obfuscate_output=False: "mocked"

    response = client.post(
        "/prompt",
        json={"prompt": "hi", "provider": "vertexai"},
        headers={"X-License-Key": "valid"},
    )

    assert response.status_code == 200
    assert response.json() == {"response": "mocked"}

    kernel.chat = original_chat
    os.environ.pop("LICENSE_KEY", None)
