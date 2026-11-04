"""Discovery and runtime selection of locally installed Ollama models."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from backend.settings import Settings


@dataclass(frozen=True)
class ModelInfo:
    name: str
    size: int | None = None
    modified_at: str | None = None

    @property
    def formatted_size(self) -> str:
        if self.size is None or self.size <= 0:
            return ""
        gb = self.size / (1024 ** 3)
        if gb >= 1.0:
            return f"{gb:.1f} GB"
        mb = self.size / (1024 ** 2)
        return f"{mb:.0f} MB"


class ModelManager:
    def __init__(self, settings: Settings | None = None, timeout: float = 5.0):
        self.settings = settings or Settings()
        self.timeout = timeout

    @property
    def ollama_url(self) -> str:
        return self.settings.get("ollama_base_url").rstrip("/")

    @staticmethod
    def find_ollama_binary() -> str | None:
        """Locates the Ollama executable on the system."""
        which_path = shutil.which("ollama")
        if which_path:
            return which_path

        candidates = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Ollama" / "ollama.exe",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Ollama" / "ollama.exe",
        ]
        for candidate in candidates:
            try:
                if candidate.is_file():
                    return str(candidate)
            except OSError:
                continue
        return None

    def is_ollama_installed(self) -> bool:
        """Returns True if the Ollama binary was found on the system."""
        return self.find_ollama_binary() is not None

    def is_ollama_running(self, url: str | None = None) -> bool:
        """Verifies if the Ollama service responds to HTTP requests."""
        target_url = (url or self.ollama_url).rstrip("/")
        try:
            response = httpx.get(f"{target_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def start_ollama_service(self, wait_timeout: float = 10.0) -> bool:
        """Attempts to start the Ollama service in the background and waits for it."""
        binary = self.find_ollama_binary() or "ollama"
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            subprocess.Popen(
                [binary, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
        except Exception:
            return False

        deadline = time.time() + wait_timeout
        while time.time() < deadline:
            if self.is_ollama_running():
                return True
            time.sleep(0.5)
        return False

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
