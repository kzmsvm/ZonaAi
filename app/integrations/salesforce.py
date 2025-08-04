"""Connector for basic Salesforce interactions.

The implementation purposefully keeps to a small subset of the Salesforce API
required for the unit tests in this kata. It demonstrates how an external
system could be authenticated with client credentials and queried for lead
data. Network errors are surfaced as ``RuntimeError`` instances so that the
integration engine can present a clean error message to API consumers.
"""

from __future__ import annotations

from typing import List

import httpx

from .base import BaseConnector


class SalesforceConnector(BaseConnector):
    """Simple connector for Salesforce using the REST API."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 5.0) -> None:
        # ``api_key`` is expected to be ``client_id:client_secret``
        self.client_id = api_key.split(":")[0]
        self.client_secret = api_key.split(":")[1] if ":" in api_key else ""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def authenticate(self) -> str:
        """Return an OAuth access token from Salesforce."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/services/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
            response.raise_for_status()
            return response.json()["access_token"]
        except httpx.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Authentication request failed: {exc}") from exc

    async def fetch_leads(self, start_date: str) -> List[dict]:
        """Fetch leads created after ``start_date`` (ISO formatted)."""
        token = await self.authenticate()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/services/data/v52.0/query",
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "q": f"SELECT Id,Name FROM Lead WHERE CreatedDate > {start_date}"
                    },
                )
            response.raise_for_status()
            return response.json().get("records", [])
        except httpx.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Lead fetch failed: {exc}") from exc

    def get_api_schema(self) -> dict:
        """Return a minimal schema used for plugin generation."""
        return {
            "endpoint": "/services/data/v52.0/query",
            "method": "GET",
            "fields": ["Id", "Name"],
        }


__all__ = ["SalesforceConnector"]

