# sAI Identity and Intelligence Layer

Implemented: 2026-11-03

## Changes

- Added `backend/identity.py` as the single maintainable source for sAI's identity and system instruction.
- Defined sAI as **Scalable AI Interface**, a free, local-first desktop assistant with the motto: **Simple AI for everyone, without charge.**
- Updated both Ollama and OpenAI-compatible providers to build the same message sequence: one system instruction, available prior conversation turns, then the current prompt.
- Updated `LLM.generate()` and `Assistant.reply()` to forward previous conversation turns to the selected provider without duplicating the current prompt.
- Added a direct, deterministic answer to the exact identity questions “What is sAI?” and “Who are you?”; other questions remain provider-routed.

## Verification

- Ollama and OpenAI-compatible request tests verify that the centralized system instruction is first and appears exactly once.
- Assistant identity test verifies the direct sAI answer.
- Assistant history test verifies prior messages are passed to the LLM.
- Existing profile-memory regression remains in the suite.
- Provider switching regression remains in the suite and both providers receive the same centralized instruction.
- A live local Ollama-backed `Assistant.reply()` request completed successfully and described sAI's free desktop-assistant purpose.
- Full suite: `venv\\Scripts\\python.exe -m unittest discover -s tests -v` — 21 passed.
- Compilation and `pip check` passed.

## Files changed

- `backend/identity.py`
- `backend/providers.py`
- `backend/llm.py`
- `backend/assistant.py`
- `tests/test_production_readiness.py`

## Notes

- No user-specific information is embedded in the system instruction.
- The system instruction is sent once per independent provider API request, as required by stateless Ollama and OpenAI-compatible chat APIs. It is not duplicated within a request.
- The UI was not changed.
