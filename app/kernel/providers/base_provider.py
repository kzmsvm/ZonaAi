from abc import ABC, abstractmethod
from typing import Dict, List


class BaseProvider(ABC):
    """Abstract base class for chat providers."""

    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from a list of chat messages."""
        raise NotImplementedError
