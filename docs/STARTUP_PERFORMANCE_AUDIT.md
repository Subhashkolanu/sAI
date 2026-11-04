# sAI Startup Responsiveness Audit

Audited: 2026-11-04
Scope: read-only trace of the launcher and desktop startup path. No runtime behavior was changed or benchmarked.

## Summary

The sidebar is constructed on the Tkinter main thread, but the event loop does not begin until all eagerly created pages finish initializing. The most likely confirmed cause of temporary unresponsiveness after the window appears is **eager Voice-page engine initialization**. The next confirmed cause is **three synchronous SQLite initializations plus an unbounded conversation-history render** during page construction. There is no startup loading state that keeps the application visibly responsive while this work completes.

## Startup execution flow

1. `run.py:259-306` loads `Settings`, preflights the selected provider, asks for Desktop GUI mode, then calls `launch_gui()`.
2. For an Ollama selection, `run.py:59-203` synchronously checks `/api/tags`, optionally starts `ollama serve`, waits for readiness, then checks the selected model. For an OpenAI-compatible selection, it only validates the saved URL shape.
3. `run.py:229-242` imports and calls `frontend.app.main()`.
4. `frontend/app.py:19-38` constructs `SAIApp` on the Tkinter main thread: settings/theme, the root window, one shared `Assistant`, sidebar, and container.
5. `Assistant()` at `backend/assistant.py:23-29` synchronously creates `LLM`, `Memory`, `ProfileMemory`, and `FileSearch`.
6. `SAIApp.create_pages()` at `frontend/app.py:40-51` eagerly constructs Chat, Voice, Memory, Search, Settings, and About pages. Vision is correctly deferred through `page_factories`.
7. `SAIApp.change_page("chat")` at `frontend/app.py:38` displays the Chat page; only after `SAIApp.__init__` returns does `frontend/app.py:79-81` enter `mainloop()` and begin processing sidebar clicks.

## Confirmed synchronous work

| Location | Work | Main Tk thread? | Likely impact |
| --- | --- | --- | --- |
| `run.py:59-110`, `run.py:126-171` | Ollama `/api/tags` HTTP checks; if unavailable, process launch plus a retry loop of up to 15 one-second waits | No GUI event loop exists yet | Delays reaching the GUI. A single unavailable check can wait 2–3 seconds; the start/retry path can take roughly 15–45 seconds depending on request timeouts. It does not explain clicks blocking after `mainloop()` starts. |
| `backend/config.py:36-47` | Creates data/assets/model/cache/log/memory/temp/upload directories while imported | Effectively startup/main thread during imports | Normally small local filesystem cost; can be slower on a delayed/locked/network-backed drive. |
| `backend/settings.py:33-47` via `frontend/app.py:21` | Reads and JSON-parses `data/settings.json` | Yes | Normally small; no network or model discovery occurs here. |
| `backend/assistant.py:26`, `backend/memory.py:24-49` | Opens SQLite, sets `busy_timeout`, changes journal mode to WAL, creates the conversation table | Yes | Potentially waits on a SQLite/file lock; connection timeout is 5 seconds. |
| `backend/assistant.py:27`, `backend/profile_memory.py:20-44` | Creates/reads `data/profile.json` | Yes | Small local I/O; file creation/write happens on first run. |
| `frontend/voice.py:28-36` | Imports `backend.speech` and instantiates `SpeechEngine` | **Yes** | Confirmed eager optional initialization. With voice dependencies present, `SpeechEngine()` calls `pyttsx3.init()` (`backend/speech.py:30-39`), which can initialize Windows speech drivers before the event loop starts. This is the highest-probability sidebar delay. With packages absent, import failure is caught but still happens synchronously. |
| `frontend/memory.py:21`, `frontend/search.py:21` | Each creates another `Memory` connection and executes SQLite setup/WAL/table creation | Yes | Repeats the SQLite setup two more times during every GUI launch. |
| `frontend/memory.py:60-82` | Calls `load_history()`: synchronous `SELECT` of every conversation and inserts every record into a `CTkTextbox` | Yes | Grows linearly with retained history and can visibly stall startup for large databases. This is a confirmed unbounded UI-thread render. |
| `frontend/app.py:40-51` | Creates all non-Vision CustomTkinter widgets and grids them | Yes | Normal widget construction cost; secondary unless the machine/font subsystem is slow. |

## Network and model-discovery findings

- No provider generation request is made by `Assistant()` or `SAIApp.create_pages()`.
- No Settings-page model discovery occurs at startup. `frontend/settings.py:103-112` runs discovery in a daemon thread only after **Refresh models** is clicked; its UI update uses `after()`.
- No Vision/OCR engine is initialized at ordinary startup. `frontend/app.py:47` defers `VisionPage`, and `frontend/vision.py:24-28` only constructs `Vision()` after the user opens that page.
- No web-search request occurs at startup.
- Chat generation already runs on a daemon thread (`frontend/chat.py:46-53`) and posts its result with `after()`.

## Root causes vs. possible causes

### Confirmed root causes

1. **Voice is eagerly initialized on the main thread.** `VoicePage` is built even when the user opens Chat first, and it constructs `SpeechEngine` synchronously.
2. **Memory is opened three times on the main thread.** One connection belongs to `Assistant`; Memory and Search pages each create another. All execute SQLite setup operations.
3. **All stored conversation records are rendered before the event loop begins.** The Memory page does this even though it is not the selected page.
4. **No usable loading state exists.** The UI neither defers work with `after()` nor disables/shows a startup status while eager page construction is running.

### Possible contributors, not confirmed by timing measurement

- SQLite WAL/table initialization may wait if another process or a previous sAI instance holds the database lock.
- `pyttsx3.init()` may be especially slow if Windows speech drivers are unavailable or degraded.
- First-run directory/profile creation and CustomTkinter/font setup can add small startup cost.
- The launcher’s Ollama preflight can make startup feel slow before the GUI is selected, but it cannot by itself block an already-running sidebar.

## Minimal recommendations, in priority order

1. **Lazy-create Voice just as Vision is already lazy-created.** Add Voice to `page_factories` and instantiate it only on first navigation. This preserves UI/features and removes optional speech-driver setup from Chat startup.
2. **Do not preload the Memory page’s history.** Create the page lazily, or defer `load_history()` until the user opens Memory. When loading, use `after()` to render small batches so sidebar events continue to be serviced.
3. **Avoid duplicate startup SQLite work.** Pass the shared Assistant memory to Memory/Search pages, or lazily create their connections on first use. Keep existing locking and close behavior.
4. **Give immediate startup feedback.** Construct the shell/sidebar and Chat page first, display a short “Loading optional features…” status, then schedule deferred page preparation with `after(0, ...)` or a background worker whose UI changes are posted through `after()`.
5. **Do not move Tk widget creation to a worker thread.** Only I/O and engine initialization should run outside the main thread; all CustomTkinter widget updates must return through `after()`.

## Suggested verification tests

- Unit test that Chat-first app construction does not instantiate `VoicePage`, `SpeechEngine`, `MemoryPage`, or `SearchPage` until their navigation target is opened.
- Callback test that sidebar navigation works while a deferred page/engine initialization is in progress; mock `after()` and a delayed initializer.
- SQLite test with a large temporary conversation database: confirm startup does not call `Memory.all()` before the Memory page is selected.
- Manual Windows check with voice dependencies installed: launch to Chat, click several sidebar buttons immediately, then open Voice and verify its status changes without freezing Chat navigation.
- Manual Windows check with a deliberately locked/large SQLite database: confirm Chat and sidebar appear first and Memory loads only on request.
- Measure time from calling `SAIApp()` to first successful sidebar click before and after changes; record machine, Python version, voice package state, and conversation count.

## Conclusion

The current delay is best explained by eager optional Voice initialization and eager Memory/Search database work, not by model discovery or Vision/OCR. The smallest safe remediation is to lazy-load Voice and non-Chat data pages, retaining all UI layouts and using `after()` only for UI updates after deferred work completes.
