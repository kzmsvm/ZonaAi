"""Basic integration engine for connecting external systems.

This module exposes FastAPI routes for adding new integrations and scanning
available systems. It is a small proof-of-concept implementation inspired by
user feedback.
"""

from typing import Dict, Type
from pathlib import Path
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.integrations.base import BaseConnector
from app.integrations.logo import LogoConnector
from app.integrations.salesforce import SalesforceConnector
from app.integrations.quickbooks import QuickBooksConnector
from app.integrations.sap import SAPConnector
from app.integrations.netsis import NetsisConnector
from app.kernel.providers.codellama import CodeLlamaProvider
from zona.plugin_manager import reload_plugins


router = APIRouter(prefix="/integrations", tags=["integrations"])

# Registry of available connector classes
CONNECTORS: Dict[str, Type[BaseConnector]] = {
    "logo": LogoConnector,
    "salesforce": SalesforceConnector,
    "quickbooks": QuickBooksConnector,
    "sap": SAPConnector,
    "netsis": NetsisConnector,
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
        token = await connector.authenticate()
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

    # Attempt to auto‑generate a plugin using CodeLlama.  This step is best
    # effort only; failures are silently ignored so that missing model files do
    # not prevent the integration from being added during tests.
    try:
        if os.getenv("CODELLAMA_MODEL") and hasattr(connector, "get_api_schema"):
            schema = connector.get_api_schema()  # type: ignore[call-arg]
            plugin_code = generate_plugin_code(request.system, schema)
            plugin_dir = Path(__file__).resolve().parent.parent / "zona" / "plugins"
            plugin_dir.mkdir(parents=True, exist_ok=True)
            (plugin_dir / f"{request.system}_plugin.py").write_text(plugin_code)
            reload_plugins()
    except Exception:  # pragma: no cover - optional feature
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


def generate_plugin_code(system: str, api_schema: dict) -> str:
    """Generate plugin source code using the CodeLlama provider.

    The prompt contains a short description of the target system along with the
    supplied API schema. Any failures (for example missing model weights) are
    propagated to the caller and handled there. This function is intentionally
    small so that unit tests can stub it if required.
    """

    provider = CodeLlamaProvider(model=os.getenv("CODELLAMA_MODEL"))
    prompt = (
        "Create a Zona plugin for {system} integration using the following API "
        "schema:\n{schema}\nThe plugin should use the PluginBase class and "
        "implement run and get_metadata methods."
    ).format(system=system, schema=api_schema)
    return provider.generate_response(prompt)
