# Task 022 — sAI Windows Installer Packaging Report

**Date:** November 4, 2026
**Project:** sAI (Scalable AI Interface) — Windows v1
**Project Path:** `D:\EXTRAS\Projects\sAI`
**Deliverable:** `sAI-Setup-v1.0.0.exe`
**Status:** Build & Validation Complete — 83/83 Tests Passing

---

## 1. Deliverable Summary

| Property | Details |
|----------|---------|
| **Installer File** | `D:\EXTRAS\Projects\sAI\dist_installer\sAI-Setup-v1.0.0.exe` |
| **Installer Size** | **39,026,072 bytes (37.2 MB)** |
| **Standalone Bundle** | `D:\EXTRAS\Projects\sAI\dist\sAI\` (`sAI.exe` + `_internal\`) |
| **Target Operating System** | Windows 10 and Windows 11 (64-bit) |
| **Application Version** | 1.0.0 |
| **Installation Mode** | Per-User Installation (`PrivilegesRequired=lowest`) |
| **Default Install Directory** | `%LOCALAPPDATA%\Programs\sAI` |
| **User Data Storage** | `%LOCALAPPDATA%\sAI\data` (Fully decoupled and preserved) |
| **PyInstaller Version** | 6.21.0 |
| **Inno Setup Version** | 6.7.3 (Command-Line Compiler `ISCC.exe`) |

---

## 2. Packaging Architecture

### 2.1 PyInstaller Standalone Bundle (`sAI.spec`)
- **Mode:** `--onedir` (relocatable application directory).
- **Subsystem:** `console=False` (GUI windowed execution, suppressing background command prompt windows).
- **Application Icon:** `assets/icon.ico` (multi-resolution 16x16 through 256x256 ICO generated directly from official `Logo.png`).
- **Bundled Resources:**
  - Embedded Python 64-bit runtime.
  - `customtkinter` fonts (`Roboto-Regular.ttf`, `Roboto-Medium.ttf`, shapes font) and theme definitions (`blue.json`).
  - Core dependencies: `darkdetect`, `PIL` (Pillow), `httpx`, `httpcore`, `python-dotenv`, `rich`, `schedule`, `ollama` client library, `sqlite3`.
  - Application assets: `Logo.png`, `assets/icon.ico`.
- **Excluded Dependencies & Data:**
  - Heavy unneeded ML/data libraries (`torch`, `torchvision`, `transformers`, `scipy`, `pandas`, `cv2`, `onnxruntime`, `numba`, etc.) were explicitly excluded, maintaining a compact 37.2 MB installer.
  - `pythoncom`, `win32com`, and `pyttsx3` excluded to avoid Python 3.14 pywin32 hook resolution conflicts (voice is disabled for v1.0.0).
  - User data, conversation databases (`*.db`), `.env`, secrets, and cache are strictly excluded from the build.
  - Ollama runtime and large model weights are **never bundled**.

### 2.2 Inno Setup Installer (`installer.iss`)
- **Architecture:** `ArchitecturesAllowed=x64compatible`, `ArchitecturesInstallIn64BitMode=x64compatible`.
- **Privilege Model:** `PrivilegesRequired=lowest`. Ordinary Windows users can install and run sAI without administrator credentials or UAC prompts.
- **Shortcuts:**
  - Start Menu shortcut: `{autoprograms}\sAI.lnk`
  - Optional Desktop shortcut: `{autodesktop}\sAI.lnk` (configurable task checkbox).
- **Compression:** Ultra-high compression using `lzma2/ultra64` with solid archive packaging.
- **Uninstaller:** Generates `{app}\unins000.exe`.

---

## 3. User Data Protection & Safety

### Decoupled Directory Structure
The installer and application maintain strict architectural separation between program binaries and mutable user data:
- **Application Binaries:** Installed into `{localappdata}\Programs\sAI`.
- **User Data Storage:** Stored into `%LOCALAPPDATA%\sAI\data`.

### Safety Guarantees
1. **Upgrade Preservation:** Reinstalling or upgrading sAI extracts exclusively to `Programs\sAI`, leaving `%LOCALAPPDATA%\sAI\data` completely untouched.
2. **Uninstall Safety:** Running `{app}\unins000.exe` uninstalls files from `Programs\sAI` only. User conversation histories (`memory.db`), preferences (`settings.json`), profiles (`profile.json`), and uploads are preserved indefinitely.
3. **No Overwrite on Conflict:** Re-running setup or installers never overwrites existing target data files.
4. **Legacy Migration:** Packaged executions safely detect any local legacy `data/` folder and copy files into `%LOCALAPPDATA%\sAI\data` non-destructively.

---

## 4. Ollama & Model Integration Policy

1. **No Silent Installation:** Ollama is not bundled and not silently installed.
2. **Onboarding Guidance:** If Ollama is absent, the First-Run Setup Wizard automatically provides the official download link (`https://ollama.com/download`) and walkthrough.
3. **Service Auto-Start:** If Ollama is installed on the system (e.g. at `%LOCALAPPDATA%\Programs\Ollama\ollama.exe`) but stopped, sAI offers a one-click button to start the background service without opening unnecessary windows (`subprocess.CREATE_NO_WINDOW`).
4. **No Automatic Model Downloads:** sAI respects user bandwidth and storage quotas by providing copyable commands (`ollama pull qwen3:4b-instruct-2507-q4_K_M`) rather than initiating multi-gigabyte background downloads.
5. **Non-Blocking Operation:** All network and service probes timeout quickly (2s) in daemon threads, preventing GUI freezing.

---

## 5. Verification & Test Results

### 5.1 Automated Quality Tests
- **Unit Test Discovery:**
  - `python -m unittest discover -s tests -v`
  - **83 tests passed in 2.442s (0 failures, 0 errors).**
- **Packaging Tests (`tests/test_packaging.py`):**
  - Spec configuration validated.
  - Inno Setup safety parameters (`PrivilegesRequired=lowest`, `{localappdata}\Programs`) validated.
  - Icon file format and resolutions validated.
  - Path separation between application and user data verified.
  - Installer and bundle existence and size verified.
- **Bytecode Compilation:**
  - `python -m compileall -q backend frontend tests run.py main.py` exited with code 0.
- **Dependency Health:**
  - `pip check` confirmed `No broken requirements found.`
- **Git Formatting:**
  - `git diff --check` passed with 0 trailing whitespace or formatting errors.

### 5.2 Standalone Execution Testing
- **Bundled `sAI.exe` Launch:** Spawning `dist\sAI\sAI.exe` initialized successfully and ran without missing DLLs or dependencies.
- **Paths Containing Spaces:** Verified successful launch from `C:\Users\kos72\AppData\Local\Temp\sAI Path With Spaces\sAI.exe`.
- **Silent Test Install:** Verified silent execution of `sAI-Setup-v1.0.0.exe` to a sandbox directory with complete file extraction.
- **Silent Test Uninstall:** Verified silent execution of `unins000.exe`, confirming complete removal of test binaries while `%LOCALAPPDATA%\sAI\data` remained 100% intact.
- **Live Ollama Assistant Chat:** Tested live prompt execution with local model `qwen3:4b-instruct-2507-q4_K_M`, receiving verified assistant response: *"Ready, listening, helping you now."*

### 5.3 Clean Machine Testing Disclosure
Testing was conducted on the development Windows 11 64-bit environment using isolated sandboxed installation directories and decoupled environment variables (`$env:PYTHONPATH=""`). An independent, bare-metal virtual machine lacking any Python installation was unavailable in this environment; clean-machine verification should be performed on a test VM prior to public distribution.

---

## 6. Release Files & Git Status

### New & Modified Configuration Files
- `sAI.spec`: PyInstaller standalone specification.
- `installer.iss`: Inno Setup compiler script.
- `BUILD_INSTRUCTIONS.md`: Complete reproduction instructions.
- `assets/icon.ico`: Multi-resolution Windows application icon.
- `tests/test_packaging.py`: Automated packaging and safety tests.
- `.gitignore`: Updated to exclude `build/`, `dist/`, and `dist_installer/`.

### Final Artifact Location
- `D:\EXTRAS\Projects\sAI\dist_installer\sAI-Setup-v1.0.0.exe` (39,026,072 bytes)

*No commits, pushes, merges, or release tags have been executed.*
