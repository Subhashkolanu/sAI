# sAI Universal Model Manager

Implemented: 2026-11-03

## Completed functionality

- `ModelManager` discovers Ollama models from the configured `/api/tags` endpoint with a bounded timeout.
- Discovery returns each reported model name, byte size, and modification timestamp.
- The original Settings page has a compact **Refresh models** action and installed-model selector; it displays installed names and available sizes.
- A model can only be selected after it appears in a discovery result. The selection persists to `data/settings.json` and updates the shared Assistant's LLM settings immediately.
- The LLM creates its provider for each request, so the next chat request uses the new selection without restarting the application or clearing conversation history.
- Ollama endpoint configuration is persisted as `ollama_base_url`; the Ollama provider uses that exact endpoint.
- OpenAI-compatible endpoints remain supported. `ModelManager.validate_openai_compatible()` reports endpoint connectivity errors and reads API keys only from the environment.
- The manager never downloads a model. Discovery and selection are explicit user actions only.

## Files modified

- `backend/config.py`
- `backend/settings.py`
- `backend/providers.py`
- `backend/model_manager.py`
- `frontend/app.py`
- `frontend/settings.py`
- `tests/test_production_readiness.py`

## Test coverage

- Discovery with name, size, and timestamp.
- Empty discovery response.
- Ollama connectivity failure.
- Valid selection, persistence, and shared-Assistant update.
- Invalid selection rejection.
- Invalid OpenAI-compatible endpoint reporting.
- Existing provider switching, system identity, conversation history, memory, and security regressions.
- Live Ollama discovery and generation are run separately against the selected installed model.

### Runtime validation

- Local discovery returned `qwen3:4b-instruct-2507-q4_K_M` and `qwen3:4b`.
- The persisted selected model is `qwen3:4b-instruct-2507-q4_K_M` at `http://127.0.0.1:11434`.
- Generation through `ProviderFactory.create(Settings().llm_config())` returned `verified` using the selected model.
- Automated suite: 27 tests passed.

## Limitations

- Only Ollama discovery is implemented. No multi-runtime discovery or hardware-aware recommendation is claimed.
- The OpenAI-compatible validation endpoint assumes the conventional `/models` route.
- GUI interaction must be manually checked on an interactive Windows desktop; no GUI claim is made by the automated tests.

## Manual testing

```powershell
cd D:\EXTRAS\Projects\sAI
ollama serve
venv\Scripts\python.exe run.py
```

Open **Settings**, click **Refresh models**, select a listed model, then send a new chat message. Restart the application and verify the same model remains selected.

Run the automated checks:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py
venv\Scripts\python.exe -m pip check
```
