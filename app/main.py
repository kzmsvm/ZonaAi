from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.kernel.zona_kernel import ZonaKernel

app = FastAPI(title="Zona API")
app.mount("/web", StaticFiles(directory="web", html=True), name="web")
kernel = ZonaKernel()


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple greeting using the kernel's obfuscation."""
    return {"message": kernel.obfuscate("Hello, Zona!")}
