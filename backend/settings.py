"""Persistent non-secret application settings."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from backend.config import (
    DATA_DIR,
    DEFAULT_PROVIDER,
    MAX_TOKENS,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    TEMPERATURE,
)


class Settings:
    """Stores user preferences without writing credentials to disk."""

    DEFAULTS = {
        "provider": DEFAULT_PROVIDER if DEFAULT_PROVIDER != "openai" else "openai_compatible",
        "ollama_model": OLLAMA_MODEL,
        "ollama_base_url": OLLAMA_BASE_URL,
        "openai_model": OPENAI_MODEL,
        "openai_base_url": OPENAI_BASE_URL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "theme": "dark",
    }

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else DATA_DIR / "settings.json"
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            return self.DEFAULTS.copy()

        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self.DEFAULTS.copy()

        data = self.DEFAULTS.copy()
        data.update({key: value for key, value in loaded.items() if key in data})
        return data

    def get(self, key):
        return self.data[key]

    def update(self, **values):
        updated = self.data.copy()
        updated.update(values)
        self._validate(updated)
        self.data = updated

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        temporary_path.replace(self.path)

    def _validate(self, data):
        if data["provider"] not in {"ollama", "openai_compatible"}:
            raise ValueError("Provider must be 'ollama' or 'openai_compatible'.")

        if data["theme"] not in {"dark", "light", "system"}:
            raise ValueError("Theme must be 'dark', 'light', or 'system'.")

        if not isinstance(data["ollama_model"], str) or not data["ollama_model"].strip():
            raise ValueError("An Ollama model is required.")

        parsed_ollama = urlparse(data["ollama_base_url"])
        if parsed_ollama.scheme not in {"http", "https"} or not parsed_ollama.netloc:
            raise ValueError("The Ollama endpoint must be an HTTP(S) URL.")

        if not isinstance(data["openai_model"], str) or not data["openai_model"].strip():
            raise ValueError("An OpenAI-compatible model is required.")

        parsed = urlparse(data["openai_base_url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("The OpenAI-compatible endpoint must be an HTTP(S) URL.")

        if not 0 <= float(data["temperature"]) <= 2:
            raise ValueError("Temperature must be between 0 and 2.")

        if int(data["max_tokens"]) < 1:
            raise ValueError("Maximum tokens must be positive.")

    def llm_config(self):
        return self.data.copy()
