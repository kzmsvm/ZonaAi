"""Tests for the proactive system implementation."""

from typing import Dict, Any

from zona.proactive.system import (
    ProactiveSystem,
    Module,
    MarketingModule,
)


class FailingModule(Module):
    """Module that raises an error when executed."""

    def __init__(self) -> None:
        super().__init__("failing")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("boom")


def test_scan_continues_after_failure() -> None:
    """The scan should continue running modules even if one fails."""

    system = ProactiveSystem()
    system.register_module(FailingModule())
    system.register_module(MarketingModule())

    result = system.scan({})

    assert result["marketing"]["status"] == "idle"
    assert result["errors"]["failing"] == "boom"

