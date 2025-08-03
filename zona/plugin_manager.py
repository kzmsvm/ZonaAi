import importlib
from typing import Optional


def handle_plugin_command(command: str) -> Optional[str]:
    if not command.startswith("!"):
        return None
    try:
        name, *args = command[1:].split(maxsplit=1)
        args_str = args[0] if args else ""
        plugin = importlib.import_module(f"zona.plugins.{name}")
        return plugin.run(args_str)
    except ModuleNotFoundError:
        return f"\u274C Plugin `{name}` not found."
    except Exception as e:
        return f"\U0001F525 Plugin `{name}` crashed: {str(e)}"
