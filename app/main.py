from fastapi import FastAPI

from app.kernel.zona_kernel import ZonaKernel

app = FastAPI(title="Zona API")
kernel = ZonaKernel()


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple greeting using the kernel's obfuscation."""
    return {"message": kernel.obfuscate("Hello, Zona!")}
