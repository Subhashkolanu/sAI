# sAI Release Readiness Report

Audited: 2026-11-03
Branch: `main` at `29f7622`
Scope: read-only code and release audit. No application code or dependencies were changed.

## Actual status

**Not release-ready as a general v1 installer.** The tested core assistant, local Ollama provider, persistent settings, memory, approval workflow, and model manager are in substantially better shape than the historical reports imply. However, the documented launcher does not honour the persisted provider/model choice, a manually entered invalid model can be saved, and there is no usable installation guide.

The working tree was clean. `data/settings.json`, `data/profile.json`, `.env`, databases, uploads, and logs are ignored; no such runtime data is tracked. A source scan found environment-variable references for API keys but no hard-coded API key or private-key material.

## Evidence collected this audit

| Check | Result |
| --- | --- |
| `venv\Scripts\python.exe -m unittest discover -s tests -v` | PASS — 27 tests |
| `venv\Scripts\python.exe -m compileall -q backend frontend tests run.py main.py` | PASS |
| `venv\Scripts\python.exe -m pip check` | PASS — no broken requirements |
| `git diff --check` | PASS |
| Import smoke: `backend.search`, file helpers, settings | PASS in the existing virtual environment |
| Live Ollama generation | Not re-run in this audit; the prior model-manager report records a successful local run. |
| GUI/hardware interaction | Not run; no claim is made. |

## Working, code-backed features

- Ollama is the default provider; the provider abstraction also supports OpenAI-compatible `/chat/completions` endpoints.
- Settings persist non-secret provider, model, endpoint, generation, and theme preferences. API keys are read only from `OPENAI_API_KEY` in the environment.
- The model manager queries Ollama `/api/tags`, exposes name/size/timestamp data, rejects undiscovered models through its selection API, persists a valid selection, and updates the shared Assistant settings.
- Assistant requests include one centralized sAI system instruction and earlier in-session history.
- Conversation memory uses SQLite WAL, a busy timeout, per-database in-process locks, and explicit close support. The concurrent-write regression passes.
- Desktop opening is restricted to a fixed set of apps/sites/folders/drives and requires `approve`; `deny` and `cancel` do not execute the pending action.
- `FileManager` confines its own operations to sAI data roots and requires explicit approval for deletion.
- Voice and Vision package imports fail gracefully when their optional requirements are absent.

## Broken or incomplete features

1. **The documented launcher ignores persisted provider and model settings.** `run.py` always checks `http://127.0.0.1:11434` and the environment/default `OLLAMA_MODEL`. It blocks startup if that model is absent, even if Settings selected a different installed model or the provider is `openai_compatible`. This breaks provider switching and persisted model selection when launched as documented.
2. **The Settings UI permits an invalid Ollama model.** The installed-model dropdown validates selection, but the editable `Ollama model` field is saved directly without discovery validation. A typo can persist and make later chat requests fail. The existing invalid-selection test covers `ModelManager`, not this UI save path.
3. **Vision is initialized during normal application construction.** `SAIApp.create_pages()` constructs `VisionPage`, and `VisionPage` constructs `easyocr.Reader` immediately. This can make ordinary chat startup depend on optional OCR initialization and gives no explicit consent boundary for any OCR model acquisition. It is not hardware-tested.
4. **Web search is not installable from the declared core requirements.** `backend/search.py` imports `requests`, `beautifulsoup4`, and `duckduckgo-search`; none is declared in `requirements-core.txt` or an optional search requirements file. The current sidebar Search page searches conversations, not the web-search engine. The About page nevertheless presents Web Search as a current feature.
5. **Automation is a standalone engine, not an integrated assistant/UI feature.** It has no command or page that creates or manages jobs. Similarly, `Database` is a separate global database layer with no demonstrated production caller.
6. **Reports and product text are stale/inconsistent.** `README.md` is an old audit, not a user guide. Historical reports disagree about UI state and old Ollama availability; `frontend/about.py` and terminal help advertise Voice, Vision, Web Search, and Automation more broadly than the tested integration supports.

## Security observations

No committed key or local user-data exposure was found. The tested approval and `FileManager` controls are effective for their call paths.

- `backend/utils.py` still exposes unrestricted `delete_file`, `copy_file`, and JSON file helpers. They are not referenced by the Assistant/UI today, so this is a **latent medium-risk API**, not a demonstrated remote/AI-triggered deletion path. Future integrations must use `FileManager` or enforce the same containment and approval rules.
- `SearchEngine.fetch_page()` blocks non-public resolved addresses and redirects, but has no response-size limit and relies on a pre-request DNS check. It is not UI-exposed today. Treat it as **not ready to expose to model-controlled URLs** without a bounded streaming fetch and redirect/DNS-safe policy.
- Desktop action approval has regression coverage, but GUI confirmation behavior has not been manually tested.

## Critical release blockers

1. Make launcher startup read the same persisted settings used by the UI and permit the selected provider; it must not require Ollama for an explicitly selected OpenAI-compatible local endpoint.
2. Prevent the Settings save path from persisting an unverified Ollama model, or present a clear recoverable validation/error flow.
3. Provide a concise, accurate README: supported Python/Windows version, core install, optional packages, Ollama install/model selection, environment-only API key policy, launch/test commands, and offline-default behavior.
4. Make Vision lazy or opt-in so normal chat startup never initializes optional OCR resources.

## Recommended minimal v1 scope

Ship **local text chat, persistent chat memory/search, settings/theme, Ollama model discovery/selection, optional OpenAI-compatible local endpoint, and approved desktop opening**. Keep Voice, Vision/OCR, web fetch/search, file-management APIs, and automation marked optional/experimental until their integration, dependency, consent, and hardware tests are complete.

## Exact implementation order

1. Fix launcher/configuration unification and add launcher tests for selected Ollama model and OpenAI-compatible mode.
2. Validate the Settings model entry against a fresh discovery result; add UI-callback tests for invalid, empty, unavailable, and valid selections.
3. Lazy-load Vision on navigation and add a dependency-absent startup regression. Do not automatically download OCR resources.
4. Correct feature claims, split or declare web-search dependencies, and replace the README with release instructions.
5. Either harden/unify unused unrestricted file helpers or clearly keep them out of all assistant routes; add tests before exposing web fetch or file operations.

## Tests required before release

- Fresh Windows virtual-environment installation using only the documented core requirements, followed by launch/import smoke test.
- Launcher integration tests: persisted selected Ollama model, Ollama unavailable, selected OpenAI-compatible endpoint, and no forced paid API use.
- Settings/model-manager UI callback tests: discovery, empty list, unavailable service, invalid typed model, valid immediate switching, and restart persistence.
- Interactive Windows GUI pass: Chat, sidebar navigation, Settings, refresh/select model, provider errors, and approve/deny/cancel.
- Live local Ollama `/api/tags` and one generation using the model selected through the Settings UI.
- Core startup with optional voice/vision/document packages both absent and installed; separate microphone, speaker, camera, and OCR manual tests.
- If web fetch is retained, tests for response size limits, redirects, private-address blocking, and DNS changes; if file helpers are exposed, containment and approval tests for every destructive route.

## Conclusion

The merged foundation is a viable base, but **do not label this build release-ready** until the four critical blockers above have been resolved and the listed launcher/UI/live-provider tests pass.
