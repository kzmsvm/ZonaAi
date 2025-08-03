from typing import Callable, Dict, List

from app.kernel.providers import BaseProvider
from app.kernel.providers.openai_provider import OpenAIProvider
from app.storage.memory_store import load_memory, save_memory, clear_memory as clear_memory_store
from app.utils.license import LicenseManager
from zona.plugin_manager import handle_plugin_command


class ZonaKernel:
    """Chat kernel with pluggable providers and session memory."""

    def __init__(
        self,
        provider: BaseProvider | None = None,
        *,
        max_messages: int | None = 20,
        max_total_length: int | None = None,
    ) -> None:
        self.provider = provider or OpenAIProvider()
        self.memory: Dict[str, List[dict[str, str]]] = load_memory()
        self.max_messages = max_messages
        self.max_total_length = max_total_length
        self.pending_actions: Dict[str, str] = {}

        self.providers: Dict[str, Callable[..., str]] = {
            "openai": self.openai_chat,
        }
        if LicenseManager.validate_license():
            self.providers["gemini"] = self.gemini_chat

    def obfuscate(self, text: str) -> str:
        return text[::-1]

    def chat(
        self,
        provider: BaseProvider,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        stripped = prompt.strip()

        if session_id in self.pending_actions:
            confirmation = stripped.lower()
            if confirmation in {"yes", "y"}:
                command = self.pending_actions.pop(session_id)
                return handle_plugin_command(command)
            if confirmation in {"no", "n"}:
                self.pending_actions.pop(session_id)
                return "Cancelled."
            return "Please reply 'yes' or 'no'."

        if stripped == "!clear":
            self.clear_memory(session_id)
            return "Memory cleared."
        if stripped == "!clear_all":
            self.clear_memory()
            return "All memory cleared."
        if stripped.startswith("!"):
            self.pending_actions[session_id] = stripped
            name, *args = stripped[1:].split(maxsplit=1)
            args_str = args[0] if args else ""
            return f"Run plugin `{name}` with args `{args_str}`? (yes/no)"

        history = self.memory.setdefault(session_id, [])
        history.append({"role": "user", "content": prompt})
        self._trim_history(history)

        content = provider.generate_response(history)

        history.append({"role": "assistant", "content": content})
        self._trim_history(history)
        save_memory(self.memory)

        return self.obfuscate(content) if obfuscate_output else content

    def dispatch_provider(
        self,
        name: str,
        prompt: str,
        session_id: str = "default",
        *,
        obfuscate_output: bool = False,
    ) -> str:
        """Dispatch chat request to a provider-specific method by name."""
        provider_func = self.providers.get(name.lower())
        if provider_func is None:
            raise ValueError(f"Unknown provider: {name}")
        return provider_func(prompt, session_id=session_id, obfuscate_output=obfuscate_output)

    def openai_chat(self, prompt: str, session_id: str = "default", *, obfuscate_output: bool = False) -> str:
        provider = OpenAIProvider()
        return self.chat(provider, prompt, session_id=session_id, obfuscate_output=obfuscate_output)

    def gemini_chat(self, prompt: str, session_id: str = "default", *, obfuscate_output: bool = False) -> str:
        content = f"Gemini: {prompt}"
        return self.obfuscate(content) if obfuscate_output else content

    def _trim_history(self, history: List[dict[str, str]]) -> None:
        if self.max_messages is not None and len(history) > self.max_messages:
            del history[:-self.max_messages]
        if self.max_total_length is not None:
            total = sum(len(item["content"]) for item in history)
            while history and total > self.max_total_length:
                removed = history.pop(0)
                total -= len(removed["content"])

    def clear_memory(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.memory.clear()
            clear_memory_store()
        else:
            self.memory.pop(session_id, None)
            save_memory(self.memory)
