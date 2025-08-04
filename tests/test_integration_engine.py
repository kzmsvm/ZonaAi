import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.integrations.logo import LogoConnector
from app.main import app


client = TestClient(app)


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_list_available_integrations():
    res = client.get("/integrations/available")
    assert res.status_code == 200
    data = res.json()
    assert "available_systems" in data
    assert "logo" in data["available_systems"]


def test_logo_authenticate(monkeypatch):
    import httpx
    import asyncio

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers=None):
            assert url == "https://example.com/auth"
            assert headers["Authorization"] == "Bearer secret"
            return DummyResponse({"access_token": "token"})

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    connector = LogoConnector(api_key="secret", base_url="https://example.com")
    token = asyncio.run(connector.authenticate())
    assert token == "token"


def test_logo_fetch_invoices(monkeypatch):
    import httpx
    import asyncio

    async def fake_authenticate(self):
        return "token"

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, headers=None, params=None):
            assert params == {"start": "2024-01-01", "end": "2024-01-31"}
            assert headers["Authorization"] == "Bearer token"
            return DummyResponse({"invoices": [{"id": 1}]})

    monkeypatch.setattr(LogoConnector, "authenticate", fake_authenticate)
    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    connector = LogoConnector(api_key="secret", base_url="https://example.com")
    invoices = asyncio.run(connector.fetch_invoices("2024-01-01", "2024-01-31"))
    assert invoices == [{"id": 1}]


def test_add_integration(monkeypatch):
    import asyncio

    async def fake_authenticate(self):
        return "token"

    monkeypatch.setattr(LogoConnector, "authenticate", fake_authenticate)

    res = client.post(
        "/integrations/add",
        json={"system": "logo", "api_key": "secret", "base_url": "https://example.com"},
    )

    assert res.status_code == 200
    assert res.json() == {"message": "logo integration added", "token": "token"}


def test_scan_systems():
    res = client.get("/integrations/scan")
    assert res.status_code == 200
    data = res.json()
    assert "detected_systems" in data
    assert isinstance(data["detected_systems"], list)
