from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.utils.logger import log_interaction
from app.utils.license import LicenseManager


app = FastAPI(title="Zona API")
kernel = ZonaKernel()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"
    obfuscate_output: bool = False
    provider: str = "openai"


@app.post("/prompt")
async def prompt_handler(
    data: Prompt,
    license_key: str | None = Header(
        default=None,
        alias=LicenseManager.HEADER_NAME,
        convert_underscores=False,
    ),
) -> dict[str, str]:
    provider = data.provider.lower()
    needs_license = provider != "openai" or data.obfuscate_output
    if needs_license:
        LicenseManager.require_license(license_key)

    method_name = kernel.providers.get(provider)
    if method_name is None:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider}' is not available.",
        )
    handler = getattr(kernel, method_name)
    result = handler(
        data.prompt,
        session_id=data.session_id,
        obfuscate_output=data.obfuscate_output,
    )
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
