# Architecture Decision Records (ADR)

Project: Uzbek Voice Generator (MVP)

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
