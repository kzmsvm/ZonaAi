from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.utils.logger import log_interaction
from app.utils.license import LicenseManager
from app.integration_engine import router as integration_router
from app.utils.security import limiter, verify_api_key


STATIC_DIR = Path(__file__).resolve().parent / "static"

# Kernel varsayılan olarak OpenAIProvider ile başlar
kernel = ZonaKernel()


# Varsayılan provider ayarı
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai").lower()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        kernel.close()


# FastAPI uygulamasını oluştur
app = FastAPI(title="Zona API", lifespan=lifespan)


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


# POST /prompt — Chat endpoint'i
@app.post("/prompt", dependencies=[Depends(verify_api_key), Depends(limiter)])
async def prompt_handler(request: Request, data: Prompt) -> dict[str, str]:
    license_key = request.headers.get(LicenseManager.HEADER_NAME)

    provider_name = data.provider.lower()
    if provider_name in {"gemini", "vertexai"}:
        LicenseManager.require_license(license_key)

    try:
        result = kernel.dispatch_provider(
            provider_name,
            data.prompt,
            session_id=data.session_id,
            obfuscate_output=data.obfuscate_output,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:  # missing client/model
        raise HTTPException(status_code=500, detail=str(exc))
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


@app.delete("/memory/{session_id}")
async def delete_memory(session_id: str) -> dict[str, str]:
    """Delete all stored messages for the given session."""
    if session_id not in kernel.memory:
        raise HTTPException(status_code=404, detail="Session not found")
    kernel.clear_memory(session_id)
    return {"status": "deleted"}


# Statik web UI mount'u
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
app.include_router(integration_router)

