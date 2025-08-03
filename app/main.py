from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.providers.openai_provider import OpenAIProvider
from app.utils.logger import log_interaction


app = FastAPI(title="Zona API")
kernel = ZonaKernel()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


class Prompt(BaseModel):
    prompt: str
    provider: str
    session_id: str = "default"
    obfuscate_output: bool = False


PROVIDERS = {"openai": OpenAIProvider}


@app.post("/prompt")
async def prompt_handler(data: Prompt) -> dict[str, str]:
    provider_cls = PROVIDERS.get(data.provider.lower())
    if provider_cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {data.provider}")
    provider = provider_cls(kernel.api_key)
    result = kernel.chat(
        provider,
        data.prompt,
        session_id=data.session_id,
        obfuscate_output=data.obfuscate_output,
    )
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
