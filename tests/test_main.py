import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_global_exception_handler() -> None:
    async def raise_error() -> None:
        raise RuntimeError("boom")

    app.add_api_route("/error", raise_error)
    response = client.get("/error")
    assert response.status_code == 500
    assert response.json() == {"detail": "boom"}
