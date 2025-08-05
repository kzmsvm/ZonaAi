import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.kernel.providers.gemini_provider import GeminiProvider


def test_gemini_provider_not_configured():
    provider = GeminiProvider(project="")
    with pytest.raises(RuntimeError):
        provider.generate_response([{"role": "user", "content": "hi"}])


def test_kernel_gemini_dispatch():
    from app.kernel.zona_kernel import ZonaKernel

    kernel = ZonaKernel()
    with pytest.raises(RuntimeError):
        kernel.dispatch_provider("gemini", "hello")
