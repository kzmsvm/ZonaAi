from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.kernel.providers.openai_provider import OpenAIProvider
from app.kernel.providers.gemini_provider import GeminiProvider
from app.utils.logger import log_interaction
from app.utils.license import LicenseManager


app = FastAPI(title="Zona API")

# Varsayılan provider ile kernel başlat
kernel = ZonaKernel(provider=OpenAIProvider())


# GET / — Obfuscate edilmiş selam
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


# Prompt input model
class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"
    obfuscate_output: bool = False
    provider: str = "openai"


# Desteklenen provider'lar
PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}

PREMIUM_PROVIDERS = {"gemini"}


# POST /prompt — Chat endpoint'i
@app.post("/prompt")
async def prompt_handler(
    data: Prompt,
    license_key: str | None = Header(default=None, alias=LicenseManager.HEADER_NAME),
) -> dict[str, str]:
    provider_name = data.provider.lower()
    provider_cls = PROVIDERS.get(provider_name)
    if provider_cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {data.provider}")

    if provider_name in PREMIUM_PROVIDERS:
        LicenseManager.require_license(license_key)

    provider = provider_cls()  # API key vb. içerden alıyor
    result = kernel.chat(
        provider,
        data.prompt,
        session_id=data.session_id,
        obfuscate_output=data.obfuscate_output,
    )
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


# Statik web UI mount'u
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
