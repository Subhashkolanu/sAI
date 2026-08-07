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

import ollama
from openai import OpenAI

from backend.config import (
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    OPENAI_API_KEY,
    TEMPERATURE,
    MAX_TOKENS,
)


SYSTEM_PROMPT = """
You are sAI, a professional AI assistant.

Rules:
1. Be accurate and honest.
2. Never invent facts.
3. If you are unsure, clearly say:
   "I'm not fully confident about this information."
4. Do not make up names, dates, places or statistics.
5. If the question is about recent news or current events,
   explain that your offline knowledge may be outdated.
6. Keep answers clear and well structured.
7. Prefer saying "I don't know" over giving incorrect information.
8. For programming questions, provide complete working code whenever possible.
"""


class LLM:

    def __init__(self):

        self.provider = DEFAULT_PROVIDER.lower()

        self.openai_client = None

        if OPENAI_API_KEY:
            self.openai_client = OpenAI(
                api_key=OPENAI_API_KEY
            )

    # --------------------------------------------------

    def generate(self, prompt: str) -> str:

        if self.provider == "ollama":
            return self._ollama(prompt)

        if self.provider == "openai":
            return self._openai(prompt)

        raise ValueError(
            f"Unknown provider: {self.provider}"
        )

    # --------------------------------------------------

    def _ollama(self, prompt: str) -> str:

        response = ollama.chat(

            model=OLLAMA_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            options={
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS,
            },
        )

        return response["message"]["content"].strip()

    # --------------------------------------------------

    def _openai(self, prompt: str) -> str:

        if self.openai_client is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        response = self.openai_client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=TEMPERATURE,
            max_output_tokens=MAX_TOKENS,
        )

        try:
            return response.output_text.strip()
        except AttributeError:
            return str(response)

    # --------------------------------------------------

    def set_provider(self, provider: str):

        provider = provider.lower()

        if provider not in ("ollama", "openai"):
            raise ValueError(
                "Provider must be 'ollama' or 'openai'."
            )

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