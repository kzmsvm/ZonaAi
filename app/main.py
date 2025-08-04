from pathlib import Path
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.kernel.providers.openai_provider import OpenAIProvider
from app.kernel.providers.gemini_provider import GeminiProvider
from app.kernel.providers.vertexai_provider import VertexAIProvider
from app.utils.logger import log_interaction
from app.utils.license import LicenseManager
from app.integration_engine import router as integration_router


STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(title="Zona API")

# Varsayılan provider ayarı
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai").lower()
_default_cls = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "vertexai": VertexAIProvider,
}.get(DEFAULT_PROVIDER, OpenAIProvider)

# Varsayılan provider ile kernel başlat
kernel = ZonaKernel(provider=_default_cls())


# GET / — Obfuscate edilmiş selam
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


# Prompt input model
class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"
    obfuscate_output: bool = False
    provider: str = DEFAULT_PROVIDER


# Desteklenen provider'lar
PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "vertexai": VertexAIProvider,
}


# POST /prompt — Chat endpoint'i
@app.post("/prompt")
async def prompt_handler(request: Request, data: Prompt) -> dict[str, str]:
    license_key = request.headers.get(LicenseManager.HEADER_NAME)

    provider_name = data.provider.lower()
    provider_cls = PROVIDERS.get(provider_name)
    if provider_cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {data.provider}")

    if provider_name in {"gemini", "vertexai"}:
        LicenseManager.require_license(license_key)

    provider = provider_cls()  # API key vb. içerden alıyor
    try:
        result = kernel.chat(
            provider,
            data.prompt,
            session_id=data.session_id,
            obfuscate_output=data.obfuscate_output,
        )
    except RuntimeError as exc:  # missing client/model
        raise HTTPException(status_code=500, detail=str(exc))
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


# Statik web UI mount'u
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
app.include_router(integration_router)
