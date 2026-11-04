"""Small provider abstraction for local-first chat generation."""

from __future__ import annotations

import os
from typing import Protocol

import httpx

from backend.identity import SYSTEM_PROMPT, provider_messages


class Provider(Protocol):
    def generate(self, prompt: str, history: list[dict] | None = None) -> str: ...


class OllamaProvider:
    def __init__(self, model: str, temperature: float, max_tokens: int, base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, history: list[dict] | None = None) -> str:
        try:
            import ollama
        except ImportError as exc:
            raise RuntimeError("Ollama support is not installed.") from exc

        response = ollama.Client(host=self.base_url).chat(
            model=self.model,
            messages=provider_messages(prompt, history),
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        )
        return response["message"]["content"].strip()


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, model: str, temperature: float, max_tokens: int):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, history: list[dict] | None = None) -> str:
        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint = f"{self.base_url}/chat/completions"
        try:
            response = httpx.post(
                endpoint,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": provider_messages(prompt, history),
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"OpenAI-compatible provider request to {endpoint} failed: {exc}"
            ) from exc


class ProviderFactory:
    @staticmethod
    def create(config: dict) -> Provider:
        provider = config["provider"]
        if provider == "ollama":
            return OllamaProvider(
                config["ollama_model"],
                float(config["temperature"]),
                int(config["max_tokens"]),
                config["ollama_base_url"],
            )
        if provider == "openai_compatible":
            return OpenAICompatibleProvider(
                config["openai_base_url"],
                config["openai_model"],
                float(config["temperature"]),
                int(config["max_tokens"]),
            )
        raise ValueError(f"Unknown provider: {provider}")

