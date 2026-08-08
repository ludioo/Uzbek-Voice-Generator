# Architecture Decision Records (ADR)

Project: Uzbek Voice Generator (MVP + Phase 2 GUI)

This file records architectural and technical decisions made during implementation.
Whenever a lasting decision is made, append a new entry using the template fields below.
Do not rewrite earlier entries; supersede them with a new dated entry if the decision changes.

---

## Entry template

Copy this block for each new decision:

```text
### ADR-XXX — Short title

- **Date:** YYYY-MM-DD
- **Decision:** What was decided.
- **Reason:** Why this choice was made.
- **Trade-offs:** What was given up or accepted.
- **Consequences:** What implementers must do (or not do) going forward.
```

Required fields for every entry: **Date**, **Decision**, **Reason**, **Trade-offs**, **Consequences**.

---

## Decisions

### ADR-001 — No Controller layer for MVP

- **Date:** 2026-08-02
- **Decision:** The UI calls the Service directly. There is no Controller layer and no `src/controllers/` package for the MVP.
- **Reason:** The MVP is a simple interactive CLI. A Controller adds indirection without clear value for a single UI that already owns prompts and user-facing errors.
- **Trade-offs:** Less ceremonial layering than the older Architecture document (which mentions Controllers). A future GUI can still call the same Service without introducing a Controller.
- **Consequences:** Phase 1+ must not create `src/controllers/`. Dependency direction for presentation is **UI → Service** only.

### ADR-002 — No `src/app/` bootstrap package

- **Date:** 2026-08-02
- **Decision:** Logging setup and application wiring stay in root `main.py` while they remain minimal. Do not create a `src/app/` bootstrap package for the MVP.
- **Reason:** YAGNI — a dedicated bootstrap package is premature for a single entrypoint.
- **Trade-offs:** `main.py` knows a small amount of wiring. Extract a helper later only if a second independent module needs the same setup.
- **Consequences:** Phase 7 wires the CLI from `main.py` and configures stdlib logging there. Do not add `logging_setup.py` or `src/app/` during the MVP unless a later ADR explicitly changes this.

### ADR-003 — Simplified flow UI → Service → Provider

- **Date:** 2026-08-02
- **Decision:** The MVP uses the simplified stack **UI → Service → Provider → External (Edge TTS)**, with Config and Models as supporting packages. This intentionally omits the Architecture document’s Presentation → Application → Service layering for MVP implementation.
- **Reason:** Align implementation with PRD simplicity and Implementation Plan v1.1. An Application/Controller layer is unnecessary for the current CLI scope.
- **Trade-offs:** `docs/architecture.md` remains temporarily out of sync with MVP practice. Syncing Architecture is a separate, approved docs task — not part of Phase 0 production work.
- **Consequences:** Implement Phases 1–10 against Implementation Plan v1.1. Do not restore Controller or Application layers without a new ADR. Agreed MVP packages: `src/config/`, `src/models/`, `src/providers/`, `src/services/`, `src/ui/`. Do not create `src/controllers/`, `src/app/`, or an empty `src/utils/` by default.

### ADR-004 — Phase 0 Architecture Validation approved

- **Date:** 2026-08-02
- **Decision:** Phase 0 (Architecture Validation) is complete and approved. Reviewer and implementer agree on **UI → Service → Provider → External**, the MVP package set (`config`, `models`, `providers`, `services`, `ui`), Implementation Plan v1.1 as the execution plan, and that Phase 1 must not create `src/controllers/`, `src/app/`, or an empty `src/utils/`. The gate to Phase 1 is open.
- **Reason:** Architecture Validation acceptance criteria were met: shared understanding of layers and folders, `docs/DECISIONS.md` seeded with ADR-001–003, no production code written in Phase 0, and explicit approval to proceed was given.
- **Trade-offs:** `docs/architecture.md` remains out of sync until a separate approved docs task; implementation follows Implementation Plan v1.1 and this ADR log.
- **Consequences:** Phase 1 (project scaffolding) may begin when explicitly requested. Do not start Phase 1 automatically; implement one phase at a time and wait for approval between phases.

### ADR-005 — Service returns GenerationResult for expected failures

- **Date:** 2026-08-03
- **Decision:** `generate_audio` always returns a `GenerationResult` for expected MVP failures (empty text, invalid filename, missing voice, config errors, TTS/save failures). It does not raise those cases to the UI layer.
- **Reason:** Gives the CLI a single thin pattern: check `success` and display `error_message` / `error_kind` without try/except sprawl for PRD §11 cases.
- **Trade-offs:** Callers must inspect `result.success`; unexpected programming bugs may still raise. Provider errors are caught at the service boundary and mapped into the result.
- **Consequences:** Phase 6+ UI must handle failures via `GenerationResult`, not by catching domain exceptions from the service for those cases.

### ADR-006 — Phase 10 MVP acceptance smoke completed

- **Date:** 2026-08-03
- **Decision:** Phase 10 acceptance smoke against PRD §15 is complete on the agent side. The MVP (Phases 0–10) is ready for final reviewer sign-off, including a human listen check that generated audio is understandable.
- **Reason:** `pytest` (20 tests) passed; Female and Male CLI generations produced non-empty MP3 files under `output/`; empty text and invalid filename failed gracefully with friendly UI messages; project structure matches the simplified UI → Service → Provider stack with no Controllers/`src/app`/`src/utils`; `docs/DECISIONS.md` ADR-001–005 are in place; README install/run/test steps remain accurate.
- **Trade-offs:** “Audio is understandable” cannot be fully verified by automation; reviewer should play one Male and one Female sample once. `docs/architecture.md` remains intentionally out of sync with MVP simplifications until a separate docs task.
- **Consequences:** No further phases in Implementation Plan v1.1. Do not start post-MVP work (GUI, batch, CSV, voice settings, multi-language, etc.) without a new approved plan. Runtime dependency remains `edge-tts` only; `pytest` stays a dev dependency.

### ADR-007 — Output filenames always normalized to `.mp3`

- **Date:** 2026-08-03
- **Decision:** After filename safety validation, the service always normalizes the output basename to end with `.mp3`: append if missing, replace any other extension, and lowercase an existing `.mp3`/`.MP3` suffix. Empty stem after normalization is rejected as invalid.
- **Reason:** Edge TTS writes MP3 bytes. Users often enter a bare name (e.g. `CO_Uzb_4`); without `.mp3`, Windows players may not open the file. Wrong extensions like `.wav` would mislabel the real format.
- **Trade-offs:** User-supplied extensions other than `.mp3` are overwritten without a warning prompt. Existing extensionless files already under `output/` are not renamed.
- **Consequences:** Keep this rule in `src/services/audio_service.py` so all callers get the same behavior. Do not treat WAV or other formats as supported save types in MVP.

### ADR-008 — CSV batch generation as UI orchestration

- **Date:** 2026-08-03
- **Decision:** Batch CSV mode is implemented in the UI layer (`src/ui/batch_csv.py`) and invoked via `python main.py --csv path.csv`. It parses UTF-8 CSV with required columns `text`, `gender`, `filename`, maps gender digits `1`/`2` to Male/Female, calls existing `generate_audio` per row, continues after row failures, overwrites existing outputs, sleeps 1.0s after each non-skipped row, and reports only light console OK/FAIL + summary counts.
- **Reason:** Users need ~100 files efficiently without a GUI. Keeping batch in UI preserves **UI → Service → Provider** and reuses validation, `.mp3` normalization, and TTS error mapping already in the service.
- **Trade-offs:** No Excel/xlsx support; interactive CLI still allows richer gender tokens while CSV is digit-strict; fixed 1s delay slows large batches but reduces Edge TTS rate-limit risk; no summary CSV/log file.
- **Consequences:** Do not move CSV parsing into the service/provider. Do not add pandas/openpyxl for MVP batch. Interactive prompts remain unchanged when `--csv` is omitted.

### ADR-009 — Batch CSV output under `output/<csv_stem>/`

- **Date:** 2026-08-03
- **Decision:** Batch mode writes MP3s under `output/<csv_stem>/`, where `<csv_stem>` is the CSV file basename without extension. Interactive mode continues to write directly under `output/`. The service accepts optional `output_subdir`, validates it as a single safe path segment, resolves under `output/`, and creates the folder with `mkdir(parents=True, exist_ok=True)` before synthesize.
- **Reason:** Keeps outputs from different CSV manifests separated and easier to find without changing CSV filename columns or interactive UX.
- **Trade-offs:** Unsafe CSV basenames abort the batch before generation; older flat files already under `output/` are not moved automatically.
- **Consequences:** Batch UI must pass `csv_path.stem` as `output_subdir`. Do not put folder paths in the CSV `filename` column. Provider remains path-agnostic.

### ADR-010 — GUI Framework Selection (CustomTkinter)

- **Date:** 2026-08-08
- **Decision:** Phase 2 Windows desktop GUI will use **CustomTkinter**. Do not build a web UI (Gradio/Flask/FastAPI+frontend) for Phase 2. Do not adopt PyQt5/PySide6 unless a later ADR supersedes this choice.
- **Reason:** The product target is a native Windows desktop app, ideally a single PyInstaller `.exe` for non-technical users. CustomTkinter sits on Tk (commonly available with CPython on Windows), stays relatively small and simple for forms (text, dropdown, file picker, progress bar), and packages more lightly than full Qt stacks for this scope. PyQt5/PySide6 offer richer widgets and polish but pull large Qt binaries and typically inflate `.exe` size and packaging complexity without a clear need for this app’s screen set. Web/Gradio was rejected because it implies a browser/server model, conflicts with “native desktop / single exe,” and is a poorer fit for offline-feeling local file workflows and Threads/GitHub distribution messaging.
- **Trade-offs:** CustomTkinter’s look-and-feel and widget set are less rich than Qt; very advanced media controls may need a small extra dependency for MP3 preview. Qt would give denser UI kits at the cost of heavier builds. A web UI would speed prototyping but would not match the stated Windows-native packaging goal.
- **Consequences:** Add `customtkinter` (and only justified preview/packaging deps) via approved dependency review. Implement GUI under `src/ui/gui/` calling existing services — no Edge TTS imports in GUI modules. PyInstaller recipes should target CustomTkinter + `edge-tts`. Document expected installer/`exe` size vs CLI-only. If packaging proves blocked by CustomTkinter specifically, open a new ADR before switching to PySide6.

### ADR-011 — Shared generation core remains Service layer (no parallel `core/` package)

- **Date:** 2026-08-08
- **Decision:** Phase 2 does **not** introduce a new top-level `core/tts_engine.py` (or `src/core/`) that duplicates TTS/CSV/output logic. CLI and GUI both continue to consume `src/services/audio_service.py` (and existing providers/config/models). Batch CSV orchestration remains UI-adjacent per ADR-008, reusable by the GUI without moving synthesis into the presentation widgets.
- **Reason:** MVP already extracted Edge TTS, validation, voice mapping, and output policy behind the service. A second “core” package would fork the architecture, fight ADR-003 package boundaries, and risk divergent filename/voice behavior between CLI and GUI.
- **Trade-offs:** Naming differs from informal “core engine” language in some planning notes; implementers must treat **Service** as the shared engine. Large GUI files may still need worker helpers under `src/ui/gui/`, which are presentation infrastructure, not a second business layer.
- **Consequences:** GUI code must call `generate_audio` (or thin wrappers around it). Do not copy Edge TTS calls into GUI. Do not relocate CSV column rules into the provider. Any true shared non-UI helper needed by both CLI batch and GUI batch may be extracted only when two callers exist and an ADR notes the move.
- **Follow-up (G4, 2026-08-08):** Friendly user copy for `GenerationResult.error_kind` moved from `src/ui/cli.py` into shared `src/ui/messages.py` (`message_for`). CLI interactive/batch and GUI single-generate both import it. Remains UI-layer presentation text (not a second service/core package). GUI generation uses `src/ui/gui/workers.py` (`GenerateWorker`: background thread + `asyncio.run(generate_audio)`), marshalled back to the CustomTkinter main thread via `after` — presentation infrastructure per this ADR, not business logic.

### ADR-012 — GUI audio preview via OS default player

- **Date:** 2026-08-08
- **Decision:** Single-text Play uses Windows `os.startfile(mp3_path)` to open the last successful output in the OS default media player. Do not add pygame, playsound, or other in-process audio libraries for Phase 2 preview.
- **Reason:** G5 needs play-before-finish, not scrubber/pause/seek. `os.startfile` is stdlib, returns immediately (no UI freeze), and keeps packaging weight aligned with ADR-010.
- **Trade-offs:** No in-app transport controls; playback depends on the user’s associated MP3 app; non-Windows ports would need a different launcher later.
- **Consequences:** Play stays disabled until a successful generate stores `_last_output_path`. Failures opening the file show a friendly dialog and are logged. Do not import providers or synthesize again for preview.

### ADR-013 — GUI open-folder uses `get_output_dir` + OS shell

- **Date:** 2026-08-08
- **Decision:** GUI “Open folder” uses `os.startfile` on `get_output_dir()` (public wrapper over the service output root). Single-text prefers the parent of `_last_output_path` when set; batch prefers `output/<csv_stem>/` via `_last_batch_dir` after a run. Do not reimplement filename/subdir validation in widgets.
- **Reason:** Keeps ADR-007/ADR-009 path policy in the service and ADR-012’s stdlib shell launch pattern for both preview and folder reveal.
- **Trade-offs:** Same OS-association dependency as Play; folder is created with `mkdir` if missing so empty `output/` can still open.
- **Consequences:** GUI must call `get_output_dir()` rather than hard-coding `output/` relative to CWD. Batch progress reporting stays in `run_batch_csv` (optional `report` callback); CLI default reporter still prints the same OK/FAIL/summary lines.

### ADR-014 — PyInstaller onefile GUI; frozen resource vs writable root

- **Date:** 2026-08-08
- **Decision:** Ship the Phase 2 GUI as a **PyInstaller onefile** Windows build (`UzbekTTS.exe`) from entry `gui_main.py` with `console=False`. When `getattr(sys, "frozen", False)`: read bundled resources (e.g. `config/voices.json`) from `sys._MEIPASS`; write `output/` under `Path(sys.executable).parent / "output"`. Unfrozen (dev) layout stays project-root via `Path(__file__).parents[…]`.
- **Reason:** Matches ADR-010 / PRD “single `.exe` / ~5 min setup.” Writing into `_MEIPASS` would lose files on exit or fail permission checks. Reading voices from beside the exe would force shipping a sidecar JSON for every release.
- **Trade-offs:** Onefile cold start is slower than onedir; unsigned builds often trip SmartScreen/AV false positives. Bundle size includes CustomTkinter + `edge-tts` stack.
- **Consequences:** Bundle `config/voices.json` as datas; `collect_all('customtkinter')`. Pin PyInstaller in `requirements-dev.txt` only. Document build, size, and AV notes in `docs/packaging.md`. Do not commit `dist/` / `build/`. Revisit onedir only via a new ADR if AV or extract bugs block distribution.
