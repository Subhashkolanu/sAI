# sAI Voice Feature: Release Decision and Technical Report (v1.0.0)

**Task:** Task 017 — sAI Voice Feature: Fix or Disable for v1.0.0
**Date:** November 4, 2026
**Auditor:** Antigravity Assistant
**Release Decision:** **VOICE DISABLED IN V1.0.0 RELEASE UI (CODE PRESERVED FOR POST-V1)**

---

## 1. Executive Summary

A comprehensive investigation of the Voice subsystem (`frontend/voice.py`, `backend/speech.py`, `requirements-voice.txt`, and Windows runtime environment) was conducted following reported unreliability (Voice page displays "Listening...", no recognized text appears, Start button remains active, and interaction cannot be confirmed).

The investigation revealed multiple architectural and dependency blockers that prevent reliable, local-first voice input and output in the current Windows environment. In strict adherence to Task 017 Step 3 instructions and sAI's local-first privacy principles:
- **Voice is disabled in the v1.0.0 release UI.**
- Its sidebar navigation button is explicitly disabled (`state="disabled"` with label `"🎤 Voice (Disabled)"`), and navigation to `"voice"` is blocked in `frontend/app.py`.
- No speech engine or audio driver is initialized during startup or normal user operation.
- Existing Voice source code (`frontend/voice.py` and `backend/speech.py`) and optional dependency declarations (`requirements-voice.txt`) are **fully preserved** for future development.
- Documentation (`README.md`, `WINDOWS_INSTALLATION.md`, `frontend/about.py`, `backend/main.py`) has been updated to honestly reflect that Voice is experimental and deferred to post-v1.0.0.

---

## 2. Root Cause Analysis

Diagnostic tracing of `frontend/voice.py` and `backend/speech.py` identified four fundamental defects:

1. **Missing PyAudio Core Dependency for Microphone Capture:**
   - `SpeechEngine.listen()` relies on `SpeechRecognition`'s `sr.Microphone()`.
   - `speech_recognition.Microphone` hard-depends on `pyaudio` for stream allocation.
   - `pyaudio` was omitted from `requirements-voice.txt` and is not present in the environment.
   - On Python 3.14 (Windows), `pyaudio` has no pre-compiled binary wheel on PyPI, requiring external C++ build tools and PortAudio header compilation. Calling `sr.Microphone()` therefore immediately raises `AttributeError: Could not find PyAudio; check installation`.

2. **Violation of Local-First Principle (Cloud Dependency):**
   - `SpeechEngine.listen()` passes captured audio to `self.recognizer.recognize_google(audio)`.
   - This service sends user audio to Google's public cloud speech recognition endpoint (`https://www.google.com/speech-api/v1/recognize`).
   - If offline, firewalled, or unauthenticated, the request raises an exception caught by a blanket `except Exception: return ""`.
   - This silent failure leaves the user with an empty string, triggering `"No speech detected"` without diagnostic feedback, and violates sAI's core principle of free, local-first, privacy-conscious operation.

3. **Offline TTS Driver Linkage Failure (`pyttsx3` on Python 3.14):**
   - `SpeechEngine.__init__` instantiates `pyttsx3.init()`.
   - On Windows, `pyttsx3` loads the SAPI5 driver which executes `import pythoncom -> import pywintypes`.
   - In Python 3.14, `pywin32` DLLs located in `site-packages/pywin32_system32` are not discovered unless explicitly registered via `os.add_dll_directory()`, raising `ModuleNotFoundError: No module named 'pywintypes'`.

4. **Incomplete UI Control Lifecycle:**
   - The UI provided only a "Start Listening" button without a "Stop Listening" or "Cancel" control.
   - When listening is active, the thread remains blocked in `adjust_for_ambient_noise` (1 second) and `recognizer.listen` (up to 15 seconds), during which the user has no control to abort.

---

## 3. Fixes Evaluated and Attempted

1. **Local PyAudio vs. Sounddevice:**
   - While `sounddevice` 0.5.5 is installed and detects the host microphone (`Microphone (AB13X USB Audio)`), `speech_recognition` cannot ingest a `sounddevice` stream without implementing a custom `AudioSource` wrapper or feeding raw numpy arrays to `whisper`.
   - Task 017 explicitly states: *"Do not add dependencies or redesign the Voice page."* Replacing the entire recognition stack with a custom Whisper-on-sounddevice engine constitutes a major architectural redesign, out of scope for a delivery stabilization mission.

2. **Offline TTS Linkage:**
   - Verified that `os.add_dll_directory` resolves `pywintypes` loading for `pyttsx3`. However, without working, local-first speech-to-text input, TTS cannot provide a functional voice conversation loop.

---

## 4. Release Decision: Voice Disabled in v1.0.0

Per Task 017 Step 3:
> *"If complete voice input and output cannot be verified reliably within this task: Disable Voice in the v1.0.0 release UI."*

### Implementation Details:
1. **Sidebar Navigation:**
   - `frontend/sidebar.py`: The Voice button is rendered with `state="disabled"` and text `"🎤 Voice (Disabled)"`.
   - `Sidebar.enable()` specifically excludes `"voice"`, ensuring runtime enable calls do not activate the button.
   - `Sidebar.change_page("voice")` returns immediately without dispatching navigation.
2. **Application Controller Guard:**
   - `frontend/app.py`: `SAIApp.change_page("voice")` guards against programmatic navigation and returns immediately. `VoicePage` is never constructed during GUI operation.
3. **Engine Initialization:**
   - No speech recognition or TTS engine is constructed or queried during normal application lifecycle.
4. **Documentation Alignment:**
   - `README.md`: Clarified that Voice is experimental and disabled in the v1.0.0 UI pending offline local speech recognition integration.
   - `WINDOWS_INSTALLATION.md`: Documented that Voice is experimental and disabled in v1.0.0.
   - `frontend/about.py`: Moved Voice from "Current Features" to "Upcoming / In Development" (*Voice Assistant (Deferred to post-v1.0.0)*).
   - `backend/main.py`: Marked Voice as Upcoming in terminal help.
5. **Code Preservation:**
   - `frontend/voice.py`, `backend/speech.py`, and `requirements-voice.txt` are completely preserved in the repository for post-v1 local offline implementation (e.g. Whisper + Sounddevice).

---

## 5. Verification and Test Results

All verification commands executed cleanly from `D:\EXTRAS\Projects\sAI`:

1. **Automated Unit Tests:**
   - Command: `python -m unittest discover -s tests -v`
   - Result: **PASS — 43 tests run, 0 failures, 0 errors in 0.517s**.
   - Added new regression coverage:
     - `test_voice_sidebar_navigation_is_disabled_in_release_ui`: Confirms Voice sidebar button is disabled and `enable()` does not re-enable it.
     - `test_change_page_voice_does_not_initialize_voice_page`: Confirms calling `change_page("voice")` does not instantiate `VoicePage`.

2. **Bytecode Compilation:**
   - Command: `python -m compileall -q backend frontend tests run.py main.py`
   - Result: **PASS — Exit code 0**.

3. **Dependency Consistency:**
   - Command: `python -m pip check`
   - Result: **PASS — No broken requirements found**.

4. **Git Formatting Check:**
   - Command: `git diff --check`
   - Result: **PASS — 0 whitespace or formatting errors**.

5. **Chat Startup & Feature Isolation:**
   - Tested application lifecycle in Python:
     - Verified app launches directly to `ChatPanel` with status `"Ready"`.
     - Verified `VoicePage` is not instantiated (`'voice' in app.pages` is `False`).
     - Verified attempting navigation to `"voice"` keeps the active page on `ChatPanel`.
     - Verified application does not depend on Voice packages for chat startup or execution.

---

## 6. Remaining Post-v1 Limitations & Roadmap

For post-v1 releases, a robust local-first Voice architecture should:
1. Replace `SpeechRecognition` + Google Cloud with `sounddevice` stream capture feeding a local quantized Whisper model (`whisper.cpp` or `faster-whisper`).
2. Provide explicit user controls: separate "Start Listening" and "Stop Listening / Cancel" buttons, with live audio level indication.
3. Standardize local offline TTS using a self-contained Windows Media Foundation or Edge TTS offline fallback.
4. Add hardware device selector (input microphone and output speaker) in Settings.
