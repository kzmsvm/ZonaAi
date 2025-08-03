from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel


app = FastAPI(title="Zona API")
kernel = ZonaKernel()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": kernel.obfuscate("Hello, Zona!")}


class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"
    obfuscate_output: bool = False


@app.post("/prompt")
async def prompt_handler(data: Prompt) -> dict[str, str]:
    result = kernel.openai_chat(
        data.prompt,
        session_id=data.session_id,
        obfuscate_output=data.obfuscate_output,
    )
    return {"response": result}


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
