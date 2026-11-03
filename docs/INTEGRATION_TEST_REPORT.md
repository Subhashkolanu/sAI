# sAI Backend Integration Test Report

Tested: 2026-11-02

## Scope

Reviewed the backend integration points for assistant routing, providers, settings, persistence, desktop approval, file access, SQLite storage, and frontend-to-backend imports. No UI redesign was performed and no paid API was called.

## Results

| Test | Modules | Result | Evidence |
| --- | --- | --- | --- |
| Core regression suite | `backend/*`, `frontend/*` integration seams | PASS | 13 `unittest` tests passed. |
| Syntax compilation | application and tests | PASS | `compileall` exited successfully. |
| Dependency consistency | active virtual environment | PASS | `pip check` reported no broken requirements. |
| Ollama service connection | `backend.providers.OllamaProvider` | BLOCKED | `ollama list` and `ollama.list()` could not connect to `127.0.0.1:11434`; no model list or generation was possible. |
| Ollama model availability and generation | `backend.providers`, `backend.llm` | NOT RUN | Blocked by unavailable local Ollama service. |
| OpenAI-compatible endpoint contract | `backend.providers.OpenAICompatibleProvider` | PASS (mock) | Verified POST target `/v1/chat/completions`, payload handling, and response extraction without external API calls. |
| Provider switching persistence | `backend.llm`, `backend.settings` | PASS | Switching to `openai_compatible` now saves to the selected settings file. |
| Conversation search/persistence | `backend.memory`, `frontend.search` | PASS | Search regression and temporary SQLite persistence tests pass. |
| Settings persistence and key handling | `backend.settings`, `frontend.settings` | PASS | Provider, models, and endpoint persist; API keys are not written to settings. |
| Desktop approval: approve | `backend.assistant`, `backend.desktop` | PASS | Action is not invoked before approval and runs once after `approve`. |
| Desktop approval: deny/cancel | `backend.assistant` | PASS | Both commands cancel the pending action without invoking it. |
| File containment/deletion approval | `backend.file_manager` | PASS | Outside-root reads and unapproved deletion raise `PermissionError`; approved in-root deletion works. |
| SQLite concurrency/lifecycle | `backend.memory`, `backend.database` | PASS | Two connections completed 20 threaded writes; locking, WAL, timeout, and idempotent close paths are covered. |
| Optional feature import boundary | `frontend.voice`, `frontend.vision` | PASS (static/import) | Optional engines are lazily imported in page initialization; core imports do not import speech/vision engines. |
| Frontend/backend routing | `frontend.chat`, `frontend.memory`, `frontend.search`, `frontend.settings` | PASS (code integration) | Chat uses `Assistant`, memory/search use `Memory`, and settings use persistent `Settings`. |

## Bugs discovered and fixed

1. `LLM.set_provider()` updated provider selection but did not persist it. It now calls `Settings.save()`.
2. The security workflow implemented `approve` and `deny`, but not the requested `cancel` alias. `cancel` now safely cancels the same pending action.
3. The Settings page allowed editing the Ollama model but not the OpenAI-compatible model. Both provider-specific model fields now persist.

## Manual hardware validation required

- Start Ollama, confirm the configured model is installed, and request a real reply.
- Microphone capture, speech recognition, text-to-speech playback, and Edge TTS audio cleanup.
- Webcam access, image capture, OCR model initialization, and preview window behavior.
- Full GUI interaction on a Windows desktop with optional feature packages absent and installed.

## Remaining blockers

- Ollama is not reachable in this test environment, so local model availability and real generation remain unverified.
- No OpenAI-compatible local server was configured; the endpoint protocol was tested only with a mock to avoid network/API usage.
- GUI and hardware tests require an interactive Windows session.

## Task 008.2: Ollama Python integration

### Diagnosis

- Persisted settings select `ollama` and the exact configured model is `qwen3:4b-instruct-2507-q4_K_M`.
- The Ollama SDK effective host is `http://127.0.0.1:11434`; no `OLLAMA_HOST` override is present.
- In the restricted execution environment, both the SDK and direct `httpx` access fail with `WinError 10013` (loopback access forbidden). This is not an sAI configuration, model-name, endpoint-construction, or exception-masking defect.
- The same project virtual environment was then run with permitted local-loopback access: `GET /api/tags` returned 200 and listed the configured model; `OllamaProvider.generate()` returned `sAI provider check`; and `Assistant.reply()` returned `assistant provider check`.

### Result

No provider source change was warranted: changing a working Ollama SDK path would be speculative. The existing `Assistant` preserves the original provider exception in its visible `Error: ...` response; it is not replaced by a generic sAI connection message. Added a regression test ensuring the exact configured model name is forwarded to `ollama.chat`.

## Exact commands

From `D:\EXTRAS\Projects\sAI`:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py
venv\Scripts\python.exe -m pip check
ollama serve
ollama pull qwen3:4b-instruct-2507-q4_K_M
venv\Scripts\python.exe run.py
```

Run optional capabilities only when needed:

```powershell
venv\Scripts\python.exe -m pip install -r requirements-voice.txt
venv\Scripts\python.exe -m pip install -r requirements-vision.txt
venv\Scripts\python.exe -m pip install -r requirements-documents.txt
```

## Verdict

**NOT READY FOR UI DEVELOPMENT** — core integration tests pass, but the default local provider has not completed a real connection/model/generation test in this environment. Re-run the Ollama checks above successfully before starting UI work.
