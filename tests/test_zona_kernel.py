import sys
from pathlib import Path

# Ensure project root is in sys.path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.kernel.zona_kernel import ZonaKernel
from app.kernel.providers.base_provider import BaseProvider


class EchoProvider(BaseProvider):
    def generate_response(self, messages):
        return messages[-1]["content"]


def test_plugin_confirmation_execute_and_isolation():
    kernel = ZonaKernel()
    kernel.clear_memory()

    response = kernel.openai_chat("!math 2+2", session_id="s1")
    assert response == "Run plugin `math` with args `2+2`? (yes/no)"
    assert kernel.pending_actions["s1"] == "!math 2+2"

    other = kernel.chat(EchoProvider(), "hi", session_id="s2")
    assert other == "hi"
    assert "s1" in kernel.pending_actions

    result = kernel.openai_chat("yes", session_id="s1")
    assert result == "\U0001F9EE Result: 4"
    assert "s1" not in kernel.pending_actions


def test_plugin_confirmation_cancel():
    kernel = ZonaKernel()
    kernel.clear_memory()

    response = kernel.openai_chat("!math 2+2", session_id="s1")
    assert response == "Run plugin `math` with args `2+2`? (yes/no)"

    result = kernel.openai_chat("no", session_id="s1")
    assert result == "Cancelled."
    assert "s1" not in kernel.pending_actions
