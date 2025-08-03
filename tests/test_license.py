import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import app.main as main
from app.kernel.zona_kernel import ZonaKernel

client = TestClient(main.app)


def test_premium_provider_without_license():
    os.environ.pop("LICENSE_KEY", None)
    original = main.kernel
    main.kernel = ZonaKernel()
    res = client.post("/prompt", json={"prompt": "hi", "provider": "gemini"})
    assert res.status_code == 403
    assert res.json()["detail"].startswith("A valid license key is required")
    main.kernel = original


def test_premium_provider_with_license():
    os.environ["LICENSE_KEY"] = "valid"
    original = main.kernel
    main.kernel = ZonaKernel()
    res = client.post(
        "/prompt",
        json={"prompt": "hi", "provider": "gemini"},
        headers={"X-License-Key": "valid"},
    )
    assert res.status_code == 500
    assert "not configured" in res.json()["detail"]
    main.kernel = original
    os.environ.pop("LICENSE_KEY", None)
