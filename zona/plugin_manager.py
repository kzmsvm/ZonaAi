import importlib
import os
from pathlib import Path
from typing import Any, Optional

from zona.plugins import PluginBase


DEFAULT_ALLOWED_PLUGINS = [
    "echo",
    "hello",
    "invoice_summary",
    "math",
    "time",
    "web_scraper",
]


def _load_allowed_plugins() -> list[str]:
    env_value = os.getenv("ZONA_ALLOWED_PLUGINS")
    if env_value:
        return [p.strip() for p in env_value.split(",") if p.strip()]

    config_path = Path(__file__).with_name("plugins_allowlist.txt")
    if config_path.exists():
        return [line.strip() for line in config_path.read_text().splitlines() if line.strip()]

    return DEFAULT_ALLOWED_PLUGINS


ALLOWED_PLUGINS = _load_allowed_plugins()


def handle_plugin_command(command: str, context: Optional[dict] = None) -> Optional[str]:
    if not command.startswith("!"):
        return None
    try:
        name, *args = command[1:].split(maxsplit=1)
        args_str = args[0] if args else ""
        if name not in ALLOWED_PLUGINS:
            return f"\u274C Plugin `{name}` is not allowed."
        module = importlib.import_module(f"zona.plugins.{name}")

        # Class-based plugin support
        plugin_obj: Any
        if hasattr(module, "Plugin") and issubclass(module.Plugin, PluginBase):
            plugin_obj = module.Plugin()
            result = plugin_obj.run(args_str, context or {})
            if isinstance(result, dict):
                return result.get("result")
            return str(result)

        # Fallback to function-based plugins
        if hasattr(module, "run"):
            return module.run(args_str)
        return f"\u274C Plugin `{name}` does not define a valid entry point."
    except ModuleNotFoundError:
        return f"\u274C Plugin `{name}` not found."
    except Exception as e:
        return f"\U0001F525 Plugin `{name}` crashed: {str(e)}"
