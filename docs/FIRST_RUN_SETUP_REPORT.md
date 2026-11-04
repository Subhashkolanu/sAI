# Task 021 — sAI First-Run Setup Report

**Date:** November 4, 2026  
**Project:** sAI (Scalable AI Interface) — Windows v1  
**Project Path:** `D:\EXTRAS\Projects\sAI`  
**Status:** Verification Complete — 76/76 Unit Tests Passing  

---

## 1. Executive Summary

Task 021 implements an accessible, non-technical **First-Run Setup Wizard** for sAI, ensuring ordinary Windows 10/11 64-bit users can download, install, connect to their local AI engine, choose an installed model, and begin chatting without manual terminal debugging or programming knowledge.

The wizard adheres strictly to sAI's core product identity:
- **Local-first & Private:** Explains that all reasoning and data stay strictly on the local machine.
- **Ollama Powered:** Seamlessly detects local Ollama installation and running service status.
- **No Automatic Downloads:** Respects bandwidth and disk storage; explains how to pull models with a one-click copyable terminal command.
- **Optional Provider Support:** Allows configuring custom OpenAI-compatible local endpoints (e.g. LM Studio, vLLM, llama.cpp).
- **Asynchronous & Non-Blocking:** All HTTP and process probes run in background daemon threads, dispatching UI updates exclusively through Tkinter's `after()` queue to prevent GUI freezing.

---

## 2. Architecture & Design

### 2.1 First-Run Detection Policy (`backend/settings.py`)

A new `needs_setup()` method in `Settings` identifies whether the onboarding wizard is required:

```python
def needs_setup(self) -> bool:
    if not self.path.exists():
        return True
    if not self.data.get("setup_completed", False):
        return True
    try:
        self._validate(self.data)
    except ValueError:
        return True
    return False
```

- **Fresh Installations:** When `settings.json` does not exist on disk, `needs_setup()` returns `True`, triggering the wizard.
- **Existing Users:** When loading an existing `settings.json` that predates the `setup_completed` flag, `_load()` treats setup as completed (`setup_completed = True`), ensuring existing users skip setup seamlessly.
- **Corrupted Configuration:** If `settings.json` is corrupted or has invalid URLs/models, `_validate()` raises an error and `needs_setup()` returns `True` to allow user correction.
- **Re-run Setup:** Users can trigger the wizard at any time via a dedicated button in the Settings page.

### 2.2 Ollama Detection & Service Management (`backend/model_manager.py`)

Centralized detection logic in `ModelManager`:
- `find_ollama_binary()`: Scans `shutil.which("ollama")` and standard Windows installation paths (`%LOCALAPPDATA%\Programs\Ollama\ollama.exe`, `%PROGRAMFILES%\Ollama\ollama.exe`).
- `is_ollama_installed()`: Returns boolean indicating whether the executable is present.
- `is_ollama_running()`: Executes a non-blocking HTTP probe against `/api/tags` with a 2-second timeout, returning `True` only on HTTP 200.
- `start_ollama_service()`: Spawns `[binary, "serve"]` using `subprocess.CREATE_NO_WINDOW` on Windows and polls until responsive or deadline.
- `ModelInfo.formatted_size`: Added human-readable byte size property (`GB`/`MB`).

---

## 3. Four-Step Wizard Breakdown (`frontend/setup_wizard.py`)

### Step 1 — Welcome
- Branded header displaying:
  - **sAI — Scalable AI Interface**
  - Motto: *Simple AI for everyone, without charge.*
- Step indicator pills highlighting progress across all 4 steps.
- Plain-English feature highlights: 100% Local-First privacy, Ollama local intelligence, native Windows desktop integration.
- "Begin Setup →" action button.

### Step 2 — AI Engine (Ollama Detection)
- Background daemon thread evaluates Ollama status and updates UI safely via `safe_after()`:
  - **Running (`✓`):** Displays green confirmation and endpoint (`http://127.0.0.1:11434`), enabling the "Next" button.
  - **Stopped (`⚠`):** Explains that Ollama is installed but the service is stopped; provides "▶ Start Ollama Service" and "🔄 Retry Connection" buttons.
  - **Missing (`❌`):** Informs user that Ollama is required; provides "🌐 Download Ollama (ollama.com)" button opening the official download page (`https://ollama.com/download`) in browser, plus a "🔄 Check Again" button.
  - **Verification Rule:** Never claims a connection succeeded without HTTP 200 verification.
- **Advanced Option:** Checkbox allows configuring an OpenAI-compatible local endpoint (URL and model identifier) with an inline connection test.

### Step 3 — Model Selection
- Asynchronously queries `discover_ollama_models()`:
  - **Models Discovered:** Dropdown menu populated with installed models. Displays formatted size (e.g. `2.5 GB`) and modification date. "Refresh Models" button available.
  - **No Models Installed:** Alert card explains that models are not downloaded automatically. Recommends `qwen3:4b-instruct-2507-q4_K_M` with a one-click "📋 Copy Command" button to copy `ollama pull qwen3:4b-instruct-2507-q4_K_M` to clipboard. "Next" button remains disabled until at least one model is discovered.

### Step 4 — Ready to Launch
- Configuration Summary Card displaying AI engine, active model, endpoint, privacy guarantee, and data storage location.
- "🚀 Launch sAI" button initiates final verification:
  - Validates connection and model existence in background thread.
  - Persists `setup_completed: True`, selected provider, and active model to `settings.json`.
  - Updates assistant runtime settings.
  - On success: Dispatches completion callback to `SAIApp`, re-enabling sidebar navigation, swapping to `ChatPanel`, and setting chat status to "Ready".
  - On failure: Displays clear error message in red with a retry option without marking setup complete.

---

## 4. UI Integration & Settings Access

- **`frontend/app.py`:**
  - Evaluates `self.settings.needs_setup()` during launch.
  - If setup is needed: Disables sidebar navigation (`self.sidebar.disable()`) and mounts `SetupWizard` into `container`.
  - On setup completion: Invokes `finish_first_run_setup()`, destroying wizard, re-enabling sidebar (`self.sidebar.enable()`), applying settings to assistant, and focusing `ChatPanel`.
- **`frontend/settings.py`:**
  - Added "Run First-Run Setup Wizard" button allowing users to re-run onboarding whenever requested.

---

## 5. Verification & Testing

### 5.1 Unit Tests (`tests/test_first_run_setup.py`)
19 new unit tests covering all required setup conditions:
- `test_first_launch_detected_when_settings_file_missing`: Fresh install triggers setup.
- `test_existing_user_skips_setup`: Pre-existing `settings.json` skips setup.
- `test_corrupted_or_invalid_settings_triggers_setup`: Invalid endpoint triggers setup for repair.
- `test_explicit_setup_completed_false_triggers_setup`: Explicit false flag triggers setup.
- `test_ollama_missing_detection`: Handles missing executable correctly.
- `test_ollama_detected_when_binary_present`: Finds binary in PATH or standard directory.
- `test_ollama_unavailable_detection`: Handles connection refused.
- `test_ollama_running_detection`: Verifies HTTP 200 response.
- `test_start_ollama_service_success`: Verifies service startup loop.
- `test_start_ollama_service_timeout_failure`: Verifies timeout handling.
- `test_empty_model_list_handling`: Handles empty model list gracefully.
- `test_model_info_formatted_size`: Formats bytes to GB/MB correctly.
- `test_model_selection_persistence`: Selected model persists to disk.
- `test_successful_setup_flow`: End-to-end setup flow completes, saves settings, invokes callback.
- `test_failed_setup_and_retry`: Verification failure displays error without marking complete.
- `test_openai_compatible_setup_flow`: Alternate OpenAI-compatible provider flow works.
- `test_existing_settings_and_memory_preserved`: Setup does not overwrite custom settings or delete SQLite conversation history.
- `test_app_displays_setup_wizard_on_first_run`: App displays wizard and disables sidebar on first launch.
- `test_app_finish_first_run_setup_restores_chat`: App restores chat and re-enables sidebar after setup.

### 5.2 Full Test Suite Execution
- **Command:** `python -m unittest discover -s tests -v`
- **Result:** **76 tests passed in 2.438s, 0 failures, 0 errors.**

### 5.3 Static Analysis & Health Checks
- **`compileall`:** Clean compilation of all modules (exit code 0).
- **`pip check`:** `No broken requirements found.`
- **Smoke Test:** All 35 application modules imported successfully with 0 errors.
- **`git diff --check`:** Zero whitespace or formatting errors.

---

## 6. Modified & Created Files Summary

| File | Status | Description |
|------|--------|-------------|
| `backend/settings.py` | Modified | Added `setup_completed` default, migration backward-compatibility, and `needs_setup()` |
| `backend/model_manager.py` | Modified | Added binary search, service running probe, service auto-start, and `formatted_size` |
| `frontend/setup_wizard.py` | Created | Four-step accessible onboarding wizard with non-blocking threads |
| `frontend/app.py` | Modified | Connected first-run detection, wizard mounting, sidebar toggling, and completion handoff |
| `frontend/settings.py` | Modified | Added "Run First-Run Setup Wizard" button and `on_run_setup` callback support |
| `tests/test_first_run_setup.py` | Created | 19 comprehensive unit tests for setup detection, wizard flow, and persistence |
| `WINDOWS_INSTALLATION.md` | Modified | Documented First-Run Setup Wizard experience, step walkthrough, and re-run instructions |
| `README.md` | Modified | Updated v1 feature list and quick-start instructions referencing setup wizard |
| `docs/FIRST_RUN_SETUP_REPORT.md` | Created | Complete implementation, architecture, and verification report |

---

## 7. Next Steps

Task 021 is complete. No Git commit, push, merge, or tag has been executed. User data files remain protected.
The project is ready for **Task 022 — Windows Installer Packaging & Distribution**.
