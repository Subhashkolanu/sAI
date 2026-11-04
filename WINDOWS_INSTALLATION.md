# Installing sAI on Windows

## Requirements

- Windows 10 or 11
- Python 3.11 or later
- PowerShell
- Ollama for the default local provider

The optional Voice, Vision, document, and web-search features have extra packages and may need a microphone, speaker, camera, or compatible local models.

## Create the Python environment

Open PowerShell and run:

```powershell
cd D:\EXTRAS\Projects\sAI
py -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` installs only the core desktop experience. Optional capability packages are deliberately separate:

```powershell
venv\Scripts\python.exe -m pip install -r requirements-voice.txt
venv\Scripts\python.exe -m pip install -r requirements-vision.txt
venv\Scripts\python.exe -m pip install -r requirements-documents.txt
venv\Scripts\python.exe -m pip install -r requirements-search.txt
```

## Set up Ollama (default local provider)

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Download a model explicitly. sAI does not download models itself:

   ```powershell
   ollama pull qwen3:4b-instruct-2507-q4_K_M
   ```

3. If Ollama is not already running, start it:

   ```powershell
   ollama serve
   ```

4. Start sAI:

   ```powershell
   venv\Scripts\python.exe run.py
   ```

Use **Settings → Refresh models** to see installed models and select one. The chosen model is saved locally and used for new messages without restarting the app.

## OpenAI-compatible local endpoint

Ollama is selected by default. To use another compatible endpoint, open **Settings**, choose `openai_compatible`, enter its base URL (usually ending in `/v1`) and model name, then save. The launcher respects this selection and does not require Ollama.

For a service that requires an API key, set it in the current PowerShell session before starting sAI:

```powershell
$env:OPENAI_API_KEY = "your-key"
venv\Scripts\python.exe run.py
```

Do not put keys in Settings, source files, or Git. A local endpoint that does not require authentication can be used without this variable. Selecting an external endpoint can send prompts to that service.

## Troubleshooting

### “Model not found”

Run `ollama list`, then either select an installed model in Settings or explicitly run `ollama pull <model-name>`. Do not edit the model field to a name that Ollama has not reported.

### “Unable to reach Ollama”

Check `ollama serve`, confirm the configured endpoint is reachable, and use **Refresh models**. A non-default Ollama endpoint must be started separately.

### Voice or Vision unavailable

Install the matching optional requirements file. Vision initializes only when the Vision page is opened. Voice Assistant is experimental and disabled in the v1.0.0 UI; its source code and requirements are preserved for future local offline speech development.

### Check the installation

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py
venv\Scripts\python.exe -m pip check
```

## Local data and privacy

sAI stores settings, conversation memory, and optional captures beneath `data\`. These are local runtime files and are ignored by Git. Desktop actions require an explicit `approve` response; `deny` or `cancel` stops the pending action.
