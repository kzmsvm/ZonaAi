import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app, kernel

client = TestClient(app)


def test_prompt_handler_returns_response():
    kernel.openai_chat = lambda prompt, session_id='default', obfuscate=False: 'mocked'
    response = client.post('/prompt', json={'prompt': 'hi'})
    assert response.status_code == 200
    assert response.json() == {'response': 'mocked'}
