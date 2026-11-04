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

## First-Run Setup Experience

When sAI launches for the first time (or when settings are not yet configured), the **First-Run Setup Wizard** guides users through initial configuration in four steps:

1. **Welcome:** Overview of sAI's local-first privacy architecture, offline intelligence, and motto ("Simple AI for everyone, without charge").
2. **AI Engine Detection:** Automatically detects whether Ollama is installed and running on your system.
   - **Running:** Connects immediately to `http://127.0.0.1:11434` and displays a green confirmation.
   - **Stopped:** If Ollama is detected on disk but not responding, provides a one-click **Start Ollama Service** button and a retry option.
   - **Missing:** If Ollama is not installed, displays an official download button opening `https://ollama.com/download` with simple instructions to install and click **Check Again**.
   - **Alternative:** Supports connecting to an OpenAI-compatible local server (such as LM Studio, vLLM, or llama.cpp) by checking the advanced toggle.
3. **Model Selection:** Discovers installed models and allows selection from a dropdown.
   - Displays model name, formatted memory size (e.g. `2.5 GB`), and modification date.
   - If no models are installed, displays clear pull guidance with a **Copy Command** button (`ollama pull qwen3:4b-instruct-2507-q4_K_M`) and a **Refresh Models** button. (sAI never downloads large model files automatically).
4. **Ready to Launch:** Verifies the connection and model one final time, persists preferences to `settings.json`, and opens the main chat interface.

The setup wizard runs automatically on first launch and does not repeat on subsequent launches. Users can re-run the wizard at any time via **Settings → Run First-Run Setup Wizard**.

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

sAI stores settings, conversation memory, and optional captures locally. These are local runtime files and are ignored by Git. Desktop actions require an explicit `approve` response; `deny` or `cancel` stops the pending action.

### User Data Storage Paths

- **Packaged Installation (`.exe`):** User data is stored in the user profile under `%LOCALAPPDATA%\sAI\data`. This ensures sAI can run safely from any directory, including protected paths, without permission issues.
- **Source Development Mode:** When running directly from source repository via `python run.py`, sAI retains the project-local `data\` directory to preserve developer workflows.
- **Custom Location Override:** To point sAI to a custom storage location, set the `SAI_DATA_DIR` environment variable before launch:
  ```powershell
  $env:SAI_DATA_DIR = "D:\MyData\sAI"
  venv\Scripts\python.exe run.py
  ```

### Automatic Legacy Data Migration

When a packaged installation runs for the first time, sAI automatically detects any existing source `data\` directory and safely copies settings, profiles, conversation history, and uploads into `%LOCALAPPDATA%\sAI\data`:
- **Non-destructive:** Original source data is never modified or deleted.
- **Conflict-safe:** Existing destination files are never overwritten.
- **Repeat-safe:** Migration can run multiple times without duplicating or corrupting data.
- **Security-safe:** `.env` files and credentials are never copied into the application data path.

### Backup Recommendation

Before performing major updates or moving installations, back up your user data directory (`%LOCALAPPDATA%\sAI\data` or local `data\`), particularly `settings.json`, `profile.json`, and the `memory\` folder containing `memory.db`.
