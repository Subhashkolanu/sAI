"""
=========================================================
sAI V1 - LLM Engine
=========================================================
Supports:
- Ollama (Offline)
- OpenAI (Online)
Automatically falls back when required.
"""

from __future__ import annotations

import os

import ollama
from openai import OpenAI

from config import (
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    OPENAI_API_KEY,
    TEMPERATURE,
    MAX_TOKENS,
)


class LLM:
    def __init__(self):
        self.provider = DEFAULT_PROVIDER.lower()

        self.openai_client = None

        if OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # --------------------------------------------------

    def generate(self, prompt: str) -> str:

        if self.provider == "ollama":
            return self._ollama(prompt)

        if self.provider == "openai":
            return self._openai(prompt)

        raise ValueError(f"Unknown provider: {self.provider}")

    # --------------------------------------------------

    def _ollama(self, prompt: str) -> str:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are sAI, a helpful, accurate and concise AI assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": TEMPERATURE,
            },
        )

        return response["message"]["content"].strip()

    # --------------------------------------------------

    def _openai(self, prompt: str) -> str:

        if self.openai_client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        response = self.openai_client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            max_output_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        try:
            return response.output_text.strip()
        except AttributeError:
            return str(response)

    # --------------------------------------------------

    def set_provider(self, provider: str):

        provider = provider.lower()

        if provider not in ("ollama", "openai"):
            raise ValueError("Provider must be 'ollama' or 'openai'.")

        self.provider = provider

    # --------------------------------------------------

    def current_provider(self):

        return self.provider

    # --------------------------------------------------

    def available(self):

        providers = []

        try:
            ollama.list()
            providers.append("ollama")
        except Exception:
            pass

        if OPENAI_API_KEY:
            providers.append("openai")

        return providers