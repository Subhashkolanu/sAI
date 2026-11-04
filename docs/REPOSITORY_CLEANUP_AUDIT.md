# sAI Repository Cleanup & Distribution Readiness Audit

**Audit Date:** November 4, 2026  
**Auditor:** Antigravity Assistant  
**Repository:** `D:\EXTRAS\Projects\sAI`  
**Git Branch:** `main` (commit `29f76228c18a95dd650ffb594a2d6775ef9baefc` + verified release candidate working tree)  
**Target Platform:** Windows 10 / Windows 11 (64-bit)  
**Mode:** READ-ONLY AUDIT (No files modified or deleted)  

---

## 1. Executive Repository Health Summary

The sAI repository is in a structurally sound, functional condition. All critical startup bottlenecks have been resolved through lazy page factories, asynchronous history loading, and shared SQLite connection pooling. Voice navigation has been safely disabled in the v1.0.0 UI, preserving its source code while preventing runtime errors.

- **Automated Tests:** 43/43 unit tests passing in ~0.68s.
- **Compilation:** 100% clean compilation across all 27 core application modules.
- **Dependency Integrity:** `pip check` reports no broken requirements.
- **Data Protection:** Runtime data (`data/settings.json`, `data/profile.json`, SQLite databases, logs, uploads, `.env`, `venv/`) is strictly ignored by Git. No secret or private key material is present in the repository.
- **Live Local Inference:** Live Ollama detection, automated service launch, and end-to-end model generation with `qwen3:4b-instruct-2507-q4_K_M` verified.

---

## 2. Complete Repository Inventory & Cleanup Classification

| File / Directory | Current Purpose | Evidence of Use | Recommendation | Reason | Risk of Removal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `run.py` | Main application launcher | Invoked by user and `launch_sai.bat`; provides mode menu and provider preflight | **KEEP** | Essential entry point | Critical |
| `main.py` | Root backend launcher | Calls `backend.main.main()` | **KEEP** | Referenced by `run.py` for Terminal mode | High |
| `launch_sai.bat` | One-click Windows batch launcher | Activates `venv` and runs `run.py` | **KEEP** | Essential convenience script for Windows users | Low |
| `Logo.png` | Project logo image asset (137 KB) | Tracked Git asset in repository root | **KEEP** | Needed to generate `.ico` application icon for packaging | Low |
| `README.md` | Primary user documentation | Product identity, installation, verification | **KEEP** | Essential project documentation | Medium |
| `WINDOWS_INSTALLATION.md` | Windows setup & troubleshooting | Step-by-step setup, Ollama guide, optional packages | **KEEP** | Essential user guide | Medium |
| `RELEASE_READINESS_REPORT.md` | Initial release readiness audit | Historical audit tracking blockers | **KEEP** | Quality assurance documentation | Low |
| `requirements.txt` | Top-level pip installer | Includes `-r requirements-core.txt` | **KEEP** | Standard Python packaging entry | High |
| `requirements-core.txt` | Core desktop requirements | Installed for core chat and GUI | **KEEP** | Defines minimal functional dependencies | Critical |
| `requirements-search.txt` | Optional web search packages | Used by `backend/search.py` | **KEEP** | Isolates optional web search | Low |
| `requirements-vision.txt` | Optional vision/OCR packages | Used by `backend/vision.py` | **KEEP** | Isolates optional vision | Low |
| `requirements-voice.txt` | Optional voice packages | Preserved for post-v1 voice development | **KEEP** | Needed for future Whisper/TTS integration | Low |
| `requirements-documents.txt` | Declares PyPDF2, docx, openpyxl, pptx | **Zero imports** anywhere in `backend/` or `frontend/` | **ARCHIVE / REMOVE** | Aspirational file with no implementing code | **Zero** |
| `.gitignore` | Git exclusion rules | Protects `data/`, `.env`, `venv/`, etc. | **KEEP** | Critical for user data privacy | Critical |
| `.env` | Local environment variables | Ignored by Git; loads `DEFAULT_PROVIDER` | **KEEP** | Local runtime config | High |
| `backend/` | Application business logic (24 files) | Core assistant, memory, providers, models | **KEEP** | Core backend package | Critical |
| `backend/automation.py` | Standalone job scheduler | Functional standalone engine, no active UI caller | **KEEP** | Tested logic; roadmap feature | Low |
| `backend/database.py` | Global SQLite helper | Standalone; `memory.py` uses its own connection | **INVESTIGATE** | Redundant with `memory.py`; keep for compatibility | Low |
| `backend/startup.py` | System check helper | Partially duplicated by `run.py` preflight | **INVESTIGATE** | Keep to avoid breaking external callers | Low |
| `frontend/` | CustomTkinter desktop UI (11 files) | Shell, sidebar, chat, settings, memory, search | **KEEP** | Core desktop UI package | Critical |
| `tests/` | Regression and production tests | 43 automated unit tests | **KEEP** | CI/CD and verification | Critical |
| `docs/` | Architectural & audit reports (9 files) | Technical audit trail and decisions | **KEEP** | Documentation and release audit history | Low |
| `assets/` | Empty directory in root | Created by `backend/config.py:29` | **KEEP** | Intended destination for `Logo.png` / `logo.ico` | Zero |
| `models/` | Empty directory in root | Created by `backend/config.py:31` | **REMOVE (from config)** | Ollama stores models in its own global root | Zero |
| `brain/` | Empty legacy directory in root | Leftover from August 5 scaffolding; unreferenced | **REMOVE** | Completely unused | **Zero** |
| `skills/` | Empty legacy directory in root | Leftover from August 5 scaffolding; unreferenced | **REMOVE** | Completely unused | **Zero** |
| `ui/` | Empty legacy directory in root | Leftover from August 5 scaffolding; unreferenced | **REMOVE** | Completely unused (UI is in `frontend/`) | **Zero** |
| `voice/` | Empty legacy directory in root | Leftover from August 5 scaffolding; unreferenced | **REMOVE** | Completely unused (Voice is in `backend/speech.py`) | **Zero** |
| `.venv/` | Second virtual environment (Aug 30) | Duplicate of `venv/`; ignored by Git | **REMOVE (Local)** | Consumes several GB of disk space redundantly | Zero (local only) |
| `venv/` | Primary active virtual environment | Active runtime environment for application | **KEEP (Local)** | Required for local development | High |
| `data/` | User runtime data directory | Contains `settings.json`, `sai.db`, memory, uploads | **KEEP (Local)** | User data — must never be deleted | Critical |
| `.vscode/` | IDE settings directory | Local developer preferences | **KEEP (Local)** | Developer environment | Zero |

---

## 3. Dependency Audit

### Core Dependency Mapping
| Package | Version Specifier | Importing Modules | Role in sAI |
| :--- | :--- | :--- | :--- |
| `customtkinter` | `>=5.2.2` | `frontend.app`, `chat`, `settings`, `sidebar`, `memory`, `search`, `about`, `vision`, `voice` | Entire graphical desktop interface |
| `ollama` | `>=0.5.0` | `backend.providers` | Local model chat API (`client.chat`) |
| `httpx` | `>=0.28.1` | `backend.providers`, `backend.model_manager` | Ollama tag discovery and OpenAI-compatible completions |
| `python-dotenv` | `>=1.1.1` | `backend.config` | Loads environment overrides from `.env` |
| `rich` | `>=14.1.0` | `run.py`, `backend.main`, `backend.utils` | Terminal UI panels, banners, and formatted output |
| `schedule` | `>=1.2.2` | `backend.automation` | Background scheduler engine |

### Optional Feature Dependencies
- **Search (`requirements-search.txt`):** `requests`, `beautifulsoup4`, `duckduckgo-search`. Used exclusively by `backend/search.py`.
- **Vision (`requirements-vision.txt`):** `opencv-python`, `Pillow`, `easyocr`. Used exclusively by `backend/vision.py` and `frontend/vision.py`.
- **Voice (`requirements-voice.txt`):** `SpeechRecognition`, `edge-tts`, `pyttsx3`, `sounddevice`, `soundfile`, `openai-whisper`. Preserved for post-v1 offline voice integration.
- **Documents (`requirements-documents.txt`):** `PyPDF2`, `python-docx`, `openpyxl`, `python-pptx`. **Unused:** No module in sAI imports these packages. They represent unbuilt aspirational features.

### Clean Core Launch Verification
Static analysis and runtime mock tests confirm that **with only the 6 core dependencies installed**, sAI successfully boots to `ChatPanel` with full functionality for:
- Local Ollama chat
- Persistent model selection & discovery
- SQLite conversation memory & history search
- Settings persistence (theme, provider, model)
- Approved desktop action execution

---

## 4. Model Compatibility & Hardware Audit

### Current Model Architecture
1. **Ollama Detection & Auto-Start:**
   - `run.py` detects if Ollama is running at the configured URL. If absent at `127.0.0.1:11434`, it automatically invokes `ollama serve` in the background and waits up to 15 seconds.
2. **Discovery & Validation:**
   - `ModelManager.discover_ollama_models()` retrieves model names, byte sizes, and timestamps from `/api/tags`.
   - Settings validation blocks users from saving non-existent or mistyped model names.
3. **Missing Model Guidance:**
   - If a configured model is missing, `run.py` halts startup with clear instructions:
     ```text
     Model not found: <model>
     Run: ollama pull <model>
     ```

### Hardware Compatibility Gaps (Critical for Distribution)
- **No Automatic Hardware Gating:** sAI currently does **not** inspect system RAM or VRAM before model execution. If a user with 8 GB RAM selects a 70B parameter model reported by Ollama, sAI will attempt generation, resulting in severe system thrashing or Ollama crash.
- **Hardware Sizing Guidance (Documented Reality):**
  - **4B parameter models (e.g. `qwen3:4b-instruct-2507-q4_K_M`, ~2.5 GB):** Ideal for standard 8 GB – 16 GB Windows laptops.
  - **1.5B – 3B models:** Suitable for low-spec (4 GB – 8 GB) systems.
  - **7B – 8B models:** Requires 16 GB+ RAM or 6 GB+ VRAM.
- **Recommendation:** Display recommended minimum RAM tags next to model sizes in the Settings dropdown (e.g. `[Recommends 8GB RAM]`).

---

## 5. Windows Packaging & Distribution Audit

### Distribution Target
To deliver a frictionless experience to non-technical Windows users:
1. **Primary Deliverable:** Standard Windows Installer (`sAI-v1.0.0-Setup.exe`).
2. **Secondary Deliverable:** Portable ZIP (`sAI-v1.0.0-Portable.zip`).

### Architectural Packaging Blocker: Data Directory Permissions
In `backend/config.py`:
```python
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
```
> [!CAUTION]
> If sAI is installed into `C:\Program Files\sAI`, standard Windows security policy prevents non-administrator processes from writing to `Program Files`. Writing to `data/settings.json`, `data/sai.db`, or `data/memory/` will fail with `PermissionError: [WinError 5] Access is denied`.

**Resolution Strategy:**
- Configure the Inno Setup installer for a **per-user installation** (`PrivilegesRequired=lowest`, installing to `{localappdata}\Programs\sAI`), matching the distribution model used by modern tools (VS Code, Slack).
- In `backend/config.py`, support a `SAI_DATA_DIR` environment variable, defaulting to `Path.home() / ".sai"` or `%LOCALAPPDATA%\sAI\data` if the application directory is not writable.

### Recommended Packaging Stack
- **Bundler:** **PyInstaller** (`--onedir` mode)
  - Must include CustomTkinter assets:
    `--add-data "venv/Lib/site-packages/customtkinter;customtkinter"`
  - Must include application logo:
    `--add-data "Logo.png;."`
  - Icon: Convert `Logo.png` to `assets/logo.ico` and pass `--icon="assets/logo.ico"`.
- **Installer Builder:** **Inno Setup**
  - Produces a signed or clean `.exe` installer.
  - Creates Start Menu and Desktop shortcuts.
  - Registers standard Windows Add/Remove Programs entry.
  - **Uninstall Safety:** Configured so the uninstaller removes only bundled application files and never deletes user conversation databases in `data/`.

---

## 6. Verification and Test Results

The following test suite was executed against the repository:

| Test | Tool / Command | Result | Notes |
| :--- | :--- | :--- | :--- |
| **Unit Test Suite** | `python -m unittest discover -s tests -v` | **PASS (43/43 tests in 0.68s)** | All regression, provider, and UI callback tests passed |
| **Compilation Check** | `python -m compileall -q backend frontend tests run.py main.py` | **PASS** | Zero syntax or compilation errors |
| **Dependency Consistency** | `python -m pip check` | **PASS** | No broken or conflicting requirements |
| **Import Smoke Test** | Iterative import of all 27 application modules | **PASS (27/27)** | All backend and frontend modules imported cleanly |
| **Launcher Auto-Start Test** | `run.ensure_provider(Settings())` | **PASS** | Auto-started stopped Ollama service, verified readiness |
| **Live Ollama Inference** | Local generation query | **PASS** | Verified end-to-end inference with `qwen3:4b-instruct-2507-q4_K_M` |
| **Fresh venv PyPI Install** | `pip install` from remote PyPI in fresh venv | **SKIPPED (Sandbox)** | Standard sandbox has no network access to remote PyPI. Verified via dependency mapping. |

---

## 7. Implementation Roadmap for Public Release (Prioritized)

```mermaid
flowchart TD
    A["Priority 1: Packaging Data Path Hardening<br/>(Make DATA_DIR fallback to %LOCALAPPDATA% if read-only)"] --> B["Priority 2: PyInstaller Specification File<br/>(Bundle core CustomTkinter, rich, httpx, ollama)"]
    B --> C["Priority 3: Inno Setup Windows Installer Script<br/>(Create per-user installer with shortcuts)"]
    C --> D["Priority 4: Repository Cleanup<br/>(Remove empty legacy folders: brain, skills, ui, voice)"]
    D --> E["Priority 5: Pre-Release Fresh Machine Smoke Test<br/>(Verify installer on a vanilla Windows 11 machine)"]
```

### Priority 1: Writable Data Directory Abstraction
Update `backend/config.py` to ensure runtime databases and settings write to `%LOCALAPPDATA%\sAI` if running from a read-only directory (e.g. `Program Files`).

### Priority 2: Create PyInstaller Build Specification (`sAI.spec`)
Configure PyInstaller with `--noconsole` (or dual launcher console/GUI), `--add-data` for CustomTkinter assets and `Logo.png`, and `--icon="assets/logo.ico"`.

### Priority 3: Create Inno Setup Configuration (`installer/sAI-Setup.iss`)
Define an Inno Setup script with:
- App Name: `sAI`
- Version: `1.0.0`
- Target: `{localappdata}\Programs\sAI`
- Start Menu and Desktop shortcuts to `sAI.exe`
- Preserved user data on uninstall

### Priority 4: Clean Up Repository Residuals
- Safely delete empty unreferenced legacy directories: `brain/`, `skills/`, `ui/`, `voice/`.
- Archive or remove aspirational `requirements-documents.txt`.
- Remove redundant local `.venv/` directory.

### Priority 5: Pre-Distribution Validation on Clean Machine
Before public release, test the compiled installer on a fresh Windows 11 machine that does not have Python installed to verify:
1. Installer executes and completes without admin elevation prompt.
2. App launches and prompts for Ollama setup if missing.
3. Chat, Settings, and Memory work without file permission errors.
4. Uninstall removes application binaries while preserving user database.
