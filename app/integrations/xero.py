from typing import List

import httpx

from .base import BaseConnector


class XeroConnector(BaseConnector):
    """Connector for Xero accounting systems."""

    def __init__(self, api_key: str, base_url: str = "https://api.xero.com", timeout: float = 5.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def authenticate(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "client_id": self.api_key,
                        "grant_type": "client_credentials",
                    },
                )
            response.raise_for_status()
            data = response.json()
            return data.get("access_token", "")
        except httpx.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Authentication request failed: {exc}") from exc

    async def fetch_invoices(self, start_date: str) -> List[dict]:
        token = await self.authenticate()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api.xro/2.0/Invoices",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"DateFrom": start_date},
                )
            response.raise_for_status()
            data = response.json()
            return data.get("Invoices", [])
        except httpx.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Invoice fetch failed: {exc}") from exc
