# sAI Release Blocker Fix Report

Implemented: 2026-11-03

## Scope

This change set implements only the five blockers recorded in `RELEASE_READINESS_REPORT.md`. The original CustomTkinter layout, provider architecture, local data, approval workflow, and optional feature boundaries were preserved. No model download, paid API call, secret, user setting, profile, upload, or database was created or committed.

## Completed fixes

### Provider and launcher configuration

- `run.py` now loads persistent `Settings` and preflights only the selected provider.
- For Ollama, it checks the saved base URL and saved model name rather than a hard-coded model. A non-default Ollama endpoint is never started by the launcher; it reports that it must be started manually.
- For `openai_compatible`, the launcher validates the saved endpoint shape and launches without requiring Ollama.
- OpenAI-compatible generation errors now identify the endpoint that failed without including an API key.

### Ollama model validation

- `ModelManager.validate_ollama_model()` centralizes installed-model validation.
- Saving Ollama settings now discovers models in a background thread before writing. An unavailable service, empty list, or unknown typed model displays an error and leaves the previously saved valid settings untouched.
- Dropdown selection retains the existing immediate shared-Assistant update behavior.

### Vision/OCR startup

- The application no longer constructs `VisionPage` while it builds the ordinary pages.
- Vision and OCR initialization occur only after the user opens the Vision page.
- The existing missing-optional-dependency message remains visible on that page.

### Documentation and installation

- Replaced the old audit-only `README.md` with an accurate product overview, core/optional install commands, privacy guidance, and verification commands.
- Added `WINDOWS_INSTALLATION.md` with Windows environment setup, explicit Ollama model setup, provider configuration, troubleshooting, and local-data guidance.

### Web search packaging and claims

- Added `requirements-search.txt` for `requests`, `beautifulsoup4`, and `duckduckgo-search` used by `backend.search`.
- Kept those packages out of core requirements because the desktop Search page performs local conversation search, not web search.
- Corrected About and terminal feature text so they do not imply an integrated web-search or automation UI.

## Files modified

- `run.py`
- `backend/model_manager.py`
- `backend/providers.py`
- `frontend/app.py`
- `frontend/settings.py`
- `frontend/about.py`
- `backend/main.py`
- `requirements.txt`
- `requirements-search.txt` (new)
- `README.md`
- `WINDOWS_INSTALLATION.md` (new)
- `tests/test_production_readiness.py`
- `docs/RELEASE_BLOCKER_FIX_REPORT.md` (new)

## Verification

Executed from `D:\EXTRAS\Projects\sAI`:

| Command | Result |
| --- | --- |
| `venv\Scripts\python.exe -m unittest discover -s tests -v` | PASS — 35 tests |
| `venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py` | PASS |
| `venv\Scripts\python.exe -m pip check` | PASS — no broken requirements |
| `git diff --check` | PASS |

New regression coverage verifies selected Ollama launcher settings, OpenAI-compatible launcher operation without Ollama, explicit OpenAI-compatible connection errors, invalid typed model rejection without persistence, successful post-discovery save, deferred Vision construction, and optional web-search package/documentation declarations.

## Live-provider testing

No paid or external endpoint was contacted. A local-only Ollama check was attempted using the selected saved model, but `http://127.0.0.1:11434` refused the connection (`WinError 10061`) at test time. The failure was correctly surfaced by `ModelManager` and was not treated as a passing generation result.

## Remaining limitations

- GUI interaction, microphone, speaker, camera, and OCR behavior still require an interactive Windows validation pass.
- A configured OpenAI-compatible endpoint was covered by launcher and provider mocks only; a real local compatible server was not available.
- The web-search helper remains optional and has no desktop UI by design; it should receive additional network-boundary tests before any model-controlled URL integration.
- Fresh-machine installation was documented but not executed in a new virtual environment during this task.

## Release verdict

**RELEASE BLOCKERS IMPLEMENTED; FINAL MANUAL VALIDATION REQUIRED.**

Before release, start Ollama, select an installed model through Settings, send a chat request, restart sAI to verify selection persistence, then perform the documented GUI/hardware checks.
