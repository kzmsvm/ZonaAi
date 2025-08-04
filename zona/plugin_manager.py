"""Dynamic plugin management for Zona.

The original project exposed a simple function that imported plugins on demand
from the ``zona.plugins`` package.  For the integration engine to generate
plugins on the fly we need a slightly more capable manager which scans the
plugin directory, honours an allow list and supports both class based and
function based plugins.

This module provides a small :class:`PluginManager` class along with a module
level :func:`handle_plugin_command` helper that preserves the previous public
API so existing code and tests continue to function.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Dict, Optional

from zona.plugins import PluginBase


DEFAULT_ALLOWED_PLUGINS = [
    "echo",
    "hello",
    "invoice_summary",
    "math",
    "time",
    "web_scraper",
]


def _load_allowed_plugins() -> set[str]:
    env_value = os.getenv("ZONA_ALLOWED_PLUGINS")
    if env_value:
        return {p.strip() for p in env_value.split(",") if p.strip()}

    config_path = Path(__file__).with_name("plugins_allowlist.txt")
    if config_path.exists():
        return {
            line.strip()
            for line in config_path.read_text().splitlines()
            if line.strip()
        }

    return set(DEFAULT_ALLOWED_PLUGINS)


class PluginManager:
    """Load and dispatch Zona plugins."""

    def __init__(self) -> None:
        self.allowlist = _load_allowed_plugins()
        self.plugins: Dict[str, Any] = {}
        self.load_plugins()

    def load_plugins(self) -> None:
        """Import plugin modules from the plugin directory.

        Both class based plugins (subclassing :class:`PluginBase`) and simple
        modules exposing a ``run`` function are supported.  Only modules listed
        in the allow list are loaded.
        """

        plugin_dir = Path(__file__).with_name("plugins")
        for path in plugin_dir.glob("*.py"):
            if path.name.startswith("__"):
                continue
            name = path.stem
            if name not in self.allowlist:
                continue
            spec = importlib.util.spec_from_file_location(f"zona.plugins.{name}", path)
            if not spec or not spec.loader:  # pragma: no cover - importlib internals
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_obj: Any | None = None
            for attr in dir(module):
                cls = getattr(module, attr)
                if (
                    isinstance(cls, type)
                    and issubclass(cls, PluginBase)
                    and cls is not PluginBase
                ):
                    plugin_obj = cls()
                    break
            if plugin_obj is None and hasattr(module, "run"):
                plugin_obj = module
            if plugin_obj is not None:
                self.plugins[name] = plugin_obj

    def handle(self, command: str, context: Optional[dict] = None) -> Optional[str]:
        if not command.startswith("!"):
            return None
        name, *args = command[1:].split(maxsplit=1)
        args_str = args[0] if args else ""

        plugin = self.plugins.get(name)
        if plugin is None:
            if name not in self.allowlist:
                return f"\u274C Plugin `{name}` is not allowed."
            return f"\u274C Plugin `{name}` not found."

        try:
            if isinstance(plugin, PluginBase):
                result = plugin.run(args_str, context or {})
                if isinstance(result, dict):
                    return str(result.get("result"))
                return str(result)
            if hasattr(plugin, "run"):
                return str(plugin.run(args_str))
            return f"\u274C Plugin `{name}` does not define a valid entry point."
        except Exception as exc:  # pragma: no cover - plugin failure
            return f"\U0001F525 Plugin `{name}` crashed: {exc}"


# Default manager used by module-level helper
_DEFAULT_MANAGER = PluginManager()


def handle_plugin_command(command: str, context: Optional[dict] = None) -> Optional[str]:
    """Backward compatible helper used throughout the project."""

    return _DEFAULT_MANAGER.handle(command, context)


__all__ = ["PluginManager", "handle_plugin_command"]

