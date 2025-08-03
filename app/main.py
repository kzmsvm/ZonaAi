from fastapi import FastAPI
from pydantic import BaseModel

from app.kernel.zona_kernel import ZonaKernel
from app.memory import MemoryStore

app = FastAPI(title="Zona API")
kernel = ZonaKernel()
memory = MemoryStore()


class Prompt(BaseModel):
    prompt: str


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple greeting using the kernel's obfuscation."""
    return {"message": kernel.obfuscate("Hello, Zona!")}


@app.post("/prompt")
async def prompt_endpoint(data: Prompt) -> dict[str, str]:
    """Process a user prompt through the kernel and store the interaction."""
    response = kernel.openai_chat(data.prompt)
    memory.add_entry(data.prompt, response)
    return {"response": response}


@app.get("/history")
async def history() -> dict[str, list[dict[str, str]]]:
    """Return the stored conversation history."""
    return {"history": memory.get_history()}
