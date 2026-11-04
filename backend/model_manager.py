"""Discovery and runtime selection of locally installed Ollama models."""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from backend.settings import Settings


@dataclass(frozen=True)
class ModelInfo:
    name: str
    size: int | None = None
    modified_at: str | None = None


class ModelManager:
    def __init__(self, settings: Settings | None = None, timeout: float = 5.0):
        self.settings = settings or Settings()
        self.timeout = timeout

    @property
    def ollama_url(self) -> str:
        return self.settings.get("ollama_base_url").rstrip("/")

    def discover_ollama_models(self) -> list[ModelInfo]:
        try:
            response = httpx.get(f"{self.ollama_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Unable to reach Ollama at {self.ollama_url}: {exc}") from exc

        return [
            ModelInfo(item["name"], item.get("size"), item.get("modified_at"))
            for item in response.json().get("models", [])
            if item.get("name")
        ]

    @staticmethod
    def validate_ollama_model(name: str, models: list[ModelInfo]) -> str:
        selected = name.strip()
        if not selected or selected not in {model.name for model in models}:
            raise ValueError("Select a model discovered from the connected Ollama service.")
        return selected

    def select_ollama_model(self, name: str, assistant=None, models: list[ModelInfo] | None = None):
        available = models if models is not None else self.discover_ollama_models()
        selected = self.validate_ollama_model(name, available)
        self.settings.update(ollama_model=selected)
        self.settings.save()
        if assistant is not None:
            assistant.llm.settings.update(ollama_model=selected)
            assistant.llm.settings.save()

    def validate_openai_compatible(self) -> str:
        base_url = self.settings.get("openai_base_url").rstrip("/")
        headers = {}
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            response = httpx.get(f"{base_url}/models", headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Unable to reach OpenAI-compatible endpoint at {base_url}: {exc}") from exc
        return "Connected"
