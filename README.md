# sAI — Scalable AI Interface

sAI is a free, local-first Windows desktop assistant built with Python and CustomTkinter. Ollama is the default provider, so normal chat can run locally without an account or paid API.

## What is included in v1

- First-run onboarding setup wizard for non-technical users
- Local Ollama chat with persistent model selection
- Optional OpenAI-compatible endpoint support
- SQLite conversation memory and local conversation search
- Theme and provider settings
- Explicitly approved desktop opening actions

Vision/OCR is optional. Voice is experimental and disabled in the v1.0.0 UI pending offline local speech recognition integration. The desktop Search page searches saved conversations; the separate web-search helper is optional and does not have a desktop UI yet. Automation is not yet exposed as an assistant or UI feature.

## Quick start on Windows

See [WINDOWS_INSTALLATION.md](WINDOWS_INSTALLATION.md) for the complete setup, first-run wizard details, and troubleshooting guide.

```powershell
cd D:\EXTRAS\Projects\sAI
py -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe run.py
```

On first launch, sAI automatically opens the **First-Run Setup Wizard** to guide you through checking Ollama and selecting an installed model.

For local chat, install Ollama and explicitly download a model you choose, for example:

```powershell
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

sAI never downloads Ollama models automatically.

## Optional packages

Install only the features you intend to use:

```powershell
venv\Scripts\python.exe -m pip install -r requirements-voice.txt
venv\Scripts\python.exe -m pip install -r requirements-vision.txt
venv\Scripts\python.exe -m pip install -r requirements-documents.txt
venv\Scripts\python.exe -m pip install -r requirements-search.txt
```

## Privacy

Settings, conversation history, and profile information stay in the local `data` directory (or `%LOCALAPPDATA%\sAI\data` for packaged installations), which is ignored by Git. API keys are never stored in settings; if an OpenAI-compatible endpoint needs one, set `OPENAI_API_KEY` in the environment. Choosing an external endpoint sends prompts to that endpoint. Ollama remains the fresh-install default.

## Verification

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py
venv\Scripts\python.exe -m pip check
```
