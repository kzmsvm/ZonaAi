from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel


app = FastAPI(title="Zona API")
kernel = ZonaKernel()


class Prompt(BaseModel):
    prompt: str
    session_id: str = "default"


@app.post("/prompt")
async def prompt_handler(data: Prompt) -> dict[str, str]:
    result = kernel.openai_chat(data.prompt, session_id=data.session_id)
    return {"response": result}


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
