"""Basic integration engine for connecting external systems.

This module exposes FastAPI routes for adding new integrations and scanning
available systems. It is a small proof-of-concept implementation inspired by
user feedback.
"""

from typing import Dict, Type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.integrations.base import BaseConnector
from app.integrations.logo import LogoConnector


router = APIRouter(prefix="/integrations", tags=["integrations"])

# Registry of available connector classes
CONNECTORS: Dict[str, Type[BaseConnector]] = {
    "logo": LogoConnector,
}


class IntegrationRequest(BaseModel):
    system: str
    api_key: str
    base_url: str


@router.post("/add")
async def add_integration(request: IntegrationRequest) -> dict:
    connector_cls = CONNECTORS.get(request.system.lower())
    if connector_cls is None:
        raise HTTPException(status_code=400, detail="Unsupported system")

    connector = connector_cls(api_key=request.api_key, base_url=request.base_url)
    try:
        token = connector.authenticate()
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(status_code=500, detail=str(exc))

    # Optional Firestore persistence if client is available
    try:  # pragma: no cover - external service
        from google.cloud import firestore  # type: ignore

        db = firestore.Client()
        db.collection("integrations").document(request.system).set(
            {
                "api_key": request.api_key,
                "base_url": request.base_url,
                "status": "active",
            }
        )
    except Exception:
        pass

    return {"message": f"{request.system} integration added", "token": token}


@router.get("/scan")
async def scan_systems() -> dict:
    systems: list[str]
    try:  # pragma: no cover - external service
        import os
        from google.cloud import asset_v1  # type: ignore

        client = asset_v1.AssetServiceClient()
        assets = client.search_all_resources(
            scope=f"projects/{os.getenv('FIRESTORE_PROJECT_ID')}",
            asset_types=[
                "cloudresourcemanager.googleapis.com/Project",
                "sqladmin.googleapis.com/Instance",
            ],
        )
        systems = [asset.asset_type for asset in assets]
    except Exception:
        systems = []
    return {"detected_systems": systems}
