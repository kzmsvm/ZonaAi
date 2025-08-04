from zona.plugins import PluginBase


class Plugin(PluginBase):
    """Echo plugin demonstrating class-based plugin API."""

    def run(self, args: str, context: dict) -> dict:
        return {"result": args}

    def get_metadata(self) -> dict:
        return {
            "name": "echo",
            "description": "Echoes the provided arguments",
            "version": "1.0",
        }
