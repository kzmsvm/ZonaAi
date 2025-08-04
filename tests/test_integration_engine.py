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


def test_logo_authenticate(monkeypatch):
    import requests

    def fake_post(url, headers, timeout):
        assert url == "https://example.com/auth"
        assert headers["Authorization"] == "Bearer secret"
        return DummyResponse({"access_token": "token"})

    monkeypatch.setattr(requests, "post", fake_post)

    connector = LogoConnector(api_key="secret", base_url="https://example.com")
    token = connector.authenticate()
    assert token == "token"


def test_logo_fetch_invoices(monkeypatch):
    import requests

    def fake_post(url, headers, timeout):
        return DummyResponse({"access_token": "token"})

    def fake_get(url, headers, params, timeout):
        assert params == {"start": "2024-01-01", "end": "2024-01-31"}
        assert headers["Authorization"] == "Bearer token"
        return DummyResponse({"invoices": [{"id": 1}]})

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "get", fake_get)

    connector = LogoConnector(api_key="secret", base_url="https://example.com")
    invoices = connector.fetch_invoices("2024-01-01", "2024-01-31")
    assert invoices == [{"id": 1}]


def test_add_integration(monkeypatch):
    monkeypatch.setattr(LogoConnector, "authenticate", lambda self: "token")

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
