from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.kernel.providers import OpenAIProvider
from app.utils.logger import log_interaction
from app.utils.license import LicenseManager


app = FastAPI(title="Zona API")
kernel = ZonaKernel(provider=OpenAIProvider())


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"
    obfuscate_output: bool = False
    provider: str = "openai"


@app.post("/prompt")

        data.prompt,
        session_id=data.session_id,
        obfuscate_output=data.obfuscate_output,
    )
    log_interaction(data.session_id, data.prompt, result)
    return {"response": result}


app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
