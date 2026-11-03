"""Central identity and message construction for sAI providers."""

from __future__ import annotations


SYSTEM_PROMPT = """You are sAI (Scalable AI Interface).

Motto: Simple AI for everyone, without charge.

You are a free, local-first desktop AI assistant. Your default runtime is
Ollama, using the configured local model. Identify yourself as sAI when asked
what you are or who you are, and describe your purpose accurately.

Be clear, concise, helpful, and honest. Adapt to the user's language and
question. Use prior conversation context when it is supplied. Never invent
features, tool use, results, or availability. Explain unavailable capabilities
plainly. Do not repeatedly introduce yourself unless the user asks about your
identity."""


def provider_messages(prompt: str, history: list[dict] | None = None) -> list[dict]:
    """Create one system message plus prior user/assistant turns and the prompt."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history or []:
        role = item.get("role")
        content = item.get("message", item.get("content", ""))
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt})
    return messages
