from abc import ABC, abstractmethod
from typing import Any, Dict


class PluginBase(ABC):
    """Base class for Zona plugins."""

    @abstractmethod
    def run(self, args: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the plugin with given args and context."""
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata such as name and version."""
        raise NotImplementedError
