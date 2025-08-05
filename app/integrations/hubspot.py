from typing import List

import httpx

from .base import BaseConnector


class HubSpotConnector(BaseConnector):
    """Connector for HubSpot CRM APIs."""

    def __init__(self, api_key: str, base_url: str = "https://api.hubapi.com", timeout: float = 5.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def authenticate(self) -> str:
        # HubSpot uses API key as bearer token; no separate authentication call
        return self.api_key

    async def fetch_contacts(self, limit: int = 100) -> List[dict]:
        token = await self.authenticate()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/crm/v3/objects/contacts",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"limit": limit},
                )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except httpx.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(f"Contact fetch failed: {exc}") from exc
