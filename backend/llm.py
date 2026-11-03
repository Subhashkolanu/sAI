"""
=========================================================
sAI V1 - LLM Engine
=========================================================
Supports:
- Ollama (Offline)
- OpenAI (Online)
Automatically falls back when required.
=========================================================
"""

from __future__ import annotations

from backend.providers import ProviderFactory
from backend.settings import Settings


class LLM:

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

    # --------------------------------------------------

    def generate(self, prompt: str, history: list[dict] | None = None) -> str:

        return ProviderFactory.create(self.settings.llm_config()).generate(prompt, history)

    # --------------------------------------------------

    def set_provider(self, provider: str):

        provider = provider.lower()
        if provider == "openai":
            provider = "openai_compatible"

        if provider not in ("ollama", "openai_compatible"):
            raise ValueError(
                "Provider must be 'ollama' or 'openai_compatible'."
            )

        self.settings.update(provider=provider)
        self.settings.save()

    # --------------------------------------------------

    def current_provider(self):

        return self.settings.get("provider")

    # --------------------------------------------------

    def available(self):

        return ["ollama", "openai_compatible"]
