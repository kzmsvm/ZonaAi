"""Basic integration engine for connecting external systems.

This module exposes FastAPI routes for adding new integrations and scanning
available systems. It is a small proof-of-concept implementation inspired by
user feedback.
"""

from typing import Dict, Type
from pathlib import Path
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import base64

try:  # Optional dependency
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # pragma: no cover - used when library is missing
    Fernet = None  # type: ignore

from app.integrations.base import BaseConnector
from app.integrations.logo import LogoConnector
from app.integrations.salesforce import SalesforceConnector
from app.integrations.quickbooks import QuickBooksConnector
from app.integrations.sap import SAPConnector
from app.integrations.netsis import NetsisConnector
from app.integrations.netsuite import NetSuiteConnector
from app.integrations.hubspot import HubSpotConnector
from app.integrations.xero import XeroConnector
from app.kernel.providers.codellama import CodeLlamaProvider
from zona.plugin_manager import reload_plugins
from app.utils.security import limiter, verify_api_key


router = APIRouter(
    prefix="/integrations",
    tags=["integrations"],
    dependencies=[Depends(verify_api_key), Depends(limiter)],
)

# Registry of available connector classes
CONNECTORS: Dict[str, Type[BaseConnector]] = {
    "logo": LogoConnector,
    "salesforce": SalesforceConnector,
    "quickbooks": QuickBooksConnector,
    "sap": SAPConnector,
    "netsis": NetsisConnector,
    "netsuite": NetSuiteConnector,
    "hubspot": HubSpotConnector,
    "xero": XeroConnector,
}


_RAW_KEY = (os.getenv("ENCRYPTION_KEY") or "default_key").encode()
if Fernet:
    # When cryptography is available, use it for encryption
    _CIPHER = Fernet(base64.urlsafe_b64encode(_RAW_KEY.ljust(32, b"0")[:32]))
else:  # pragma: no cover - simple fallback
    _CIPHER = None


def _xor(data: bytes) -> bytes:
    return bytes(b ^ _RAW_KEY[i % len(_RAW_KEY)] for i, b in enumerate(data))


def encrypt_value(value: str) -> str:
    """Encrypt a string before persisting."""
    if _CIPHER:
        return _CIPHER.encrypt(value.encode()).decode()
    return base64.urlsafe_b64encode(_xor(value.encode())).decode()


def decrypt_value(value: str) -> str:
    """Decrypt a stored string if possible."""
    try:
        if _CIPHER:
            return _CIPHER.decrypt(value.encode()).decode()
        return _xor(base64.urlsafe_b64decode(value.encode())).decode()
    except Exception:
        return value


class IntegrationRequest(BaseModel):
    system: str
    api_key: str
    base_url: str


@router.get("/available")
async def list_available_integrations() -> dict:
    """Return a list of systems that can be integrated."""
    return {"available_systems": sorted(CONNECTORS.keys())}


@router.post("/add")
async def add_integration(payload: IntegrationRequest) -> dict:
    connector_cls = CONNECTORS.get(payload.system.lower())
    if connector_cls is None:
        raise HTTPException(status_code=400, detail="Unsupported system")

    api_key = decrypt_value(payload.api_key)
    base_url = decrypt_value(payload.base_url)

    connector = connector_cls(api_key=api_key, base_url=base_url)
    try:
        token = await connector.authenticate()
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(status_code=500, detail=str(exc))

    # Optional Firestore persistence if client is available
    try:  # pragma: no cover - external service
        from google.cloud import firestore  # type: ignore

        db = firestore.Client()
        db.collection("integrations").document(payload.system).set(
            {
                "api_key": encrypt_value(api_key),
                "base_url": encrypt_value(base_url),
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
            plugin_code = generate_plugin_code(payload.system, schema)
            plugin_dir = Path(__file__).resolve().parent.parent / "zona" / "plugins"
            plugin_dir.mkdir(parents=True, exist_ok=True)
            (plugin_dir / f"{payload.system}_plugin.py").write_text(plugin_code)
            reload_plugins()
    except Exception:  # pragma: no cover - optional feature
        pass

    return {"message": f"{payload.system} integration added", "token": token}


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
