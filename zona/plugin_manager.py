import importlib
from typing import Any, Optional

from zona.plugins import PluginBase


def handle_plugin_command(command: str, context: Optional[dict] = None) -> Optional[str]:
    if not command.startswith("!"):
        return None
    try:
        name, *args = command[1:].split(maxsplit=1)
        args_str = args[0] if args else ""
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
