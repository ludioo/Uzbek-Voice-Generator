# Implementation Plan — Uzbek Voice Generator

| Field | Value |
| --- | --- |
| **Version** | 1.1 |
| **Status** | MVP complete · Phase 2 GUI complete (G0–G10) |
| **Product** | Uzbek Voice Generator (MVP) |
| **Sources of truth** | [PRD](prd.md), [Architecture](architecture.md), [Cursor Rules](cursor_rules.md); architectural simplifications recorded in [DECISIONS.md](DECISIONS.md) (to be created) |
| **Platform** | Windows · Python 3.12 · CLI first |
| **TTS** | Microsoft Edge TTS via `edge-tts` |

---

## Overview

This plan delivers the MVP defined in the PRD: a lightweight CLI that converts Uzbek text to MP3 speech using Edge TTS, with Male (`uz-UZ-SardorNeural`) and Female (`uz-UZ-MadinaNeural`) voices loaded from `config/voices.json`.

Application dependency flow for MVP (intentionally simplified vs. older Architecture mentions of Controllers / Application layer — record in `docs/DECISIONS.md`; ARCHITECTURE.md sync is a separate approved docs task if needed):

```text
UI (CLI) → Service → Provider → External (Edge TTS)
```

No Controllers, no `src/app/`, no Provider Interface, DI, or plugin systems. The only runtime dependency for MVP is `edge-tts` (plus its transitive dependencies). `pytest` is a **dev** dependency, introduced when automated tests begin (alongside functional phases and/or the light consolidation phase).

**Do not start production coding until Phase 0 (Architecture Validation) and this plan are reviewed and approved.** Implement one phase at a time; wait for approval between phases per Cursor Rules.

---

## Principles

1. **Small phases** — each phase is independently reviewable and testable.
2. **Risk-minimizing order** — architecture validation → scaffolding → pure models → config → thin provider → service → CLI → wiring → hardening → test consolidation → acceptance.
3. **Simplified layer compliance** — dependencies flow **UI → Service → Provider → External** only; no upward or sideways imports that bypass the stack.
4. **No premature abstraction** — no Controller, no `src/app/`, no Provider Interface, DI container, or plugin system in MVP.
5. **Utils only when shared** — create a utility module **only when at least two independent modules** need the same functionality. Do not create `helpers.py`, `common.py`, or an empty `src/utils/` dumping ground. Prefer private helpers in the owning module (e.g. path validation stays in the service). Prefer configuring logging in `main.py`; extract a logging helper only if/when a second independent module needs the same setup.
6. **Exceptions near the source** — prefer raising meaningful errors in the module that detects them; do not invent `exceptions.py` / `messages.py` sprawl unless splitting clearly reduces clutter.
7. **Config over hardcoding** — voice IDs live in `config/voices.json`, not in business logic.
8. **Stdlib first** — prefer `pathlib`, `logging`, `asyncio`, `dataclasses`, `json`; justify any new dependency.
9. **DECISIONS.md as ADR** — whenever an architectural or technical decision is made, append an entry to `docs/DECISIONS.md` with: **Date**, **Decision**, **Reason**, **Trade-offs**, **Consequences**.
10. **Testing evolves with implementation** — each phase that adds meaningful functionality includes Acceptance Criteria, Manual Tests, and Suggested Unit Tests (when applicable). Do not defer all tests to a final mega-phase.
11. **PRD fidelity** — do not invent requirements; GUI, batch, CSV, rate/pitch/volume are out of scope.
12. **YAGNI** — prefer a single `generation.py` models module if small; prefer a function over a class for the provider unless a class adds clear value; keep path validation private in the service rather than creating `utils/paths.py`.

---

## Current repo state (planning baseline)

| Item | State |
| --- | --- |
| Docs | Live under `docs/` (`prd.md`, `architecture.md`, `cursor_rules.md`, this plan) |
| `docs/DECISIONS.md` | **Not yet present** — required by Phase 0 |
| `config/voices.json` | Exists with Male/Female Uzbek neural voices |
| `main.py` | Stub that calls `edge_tts.Communicate` and writes `output/test.mp3` |
| `requirements.txt` | Present but empty |
| `.venv` | Exists with `edge-tts` installed |
| `src/`, `tests/`, `README.md` | Not yet present |

---

## Phase dependencies

```text
0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10
```

Each phase **must** complete and be approved before the next begins. **Phase 0 produces no production code.** Implementation (Phase 1+) must not begin until Architecture Validation and this plan are approved.

---

## Phase 0 — Architecture Validation (no production code)

### Goal

Verify shared understanding of layers, dependency direction, module responsibilities, folder structure, and data flow **before** any scaffolding or feature code. Confirm the MVP simplification: **UI → Service → Provider → External**.

### Scope / what to build

- Summarize (in review notes / this phase deliverable) the simplified architecture:
  - **UI** — prompts, status, user-facing errors; calls service only.
  - **Service** — validation, voice resolution from config, output path policy, orchestration of provider call, `GenerationResult`.
  - **Provider** — thin Edge TTS integration only.
  - **Config** — load/validate `voices.json`.
  - **Models** — pure data (`Voice`, request/result).
- Confirm folder structure for MVP scaffolding (Phase 1): `src/config/`, `src/models/`, `src/providers/`, `src/services/`, `src/ui/` — **not** `src/controllers/`, `src/app/`, or `src/utils/` unless a real shared need appears later.
- Create `docs/DECISIONS.md` with an empty template (Date / Decision / Reason / Trade-offs / Consequences) **and** seed initial entries for this review, at minimum:
  - No Controller layer for MVP (UI calls Service directly).
  - No `src/app/` bootstrap package (logging/wiring stay in `main.py` when minimal).
  - Simplified flow UI → Service → Provider; document that this intentionally simplifies relative to older Architecture Controller / Application-layer mentions; ARCHITECTURE.md sync is a separate approved docs task if needed.
- No production Python packages or feature code.

### Files to create

- `docs/DECISIONS.md` (template + initial simplification decisions)

### Files to modify

- None required (do not rewrite `architecture.md` in this phase)

### Explicitly out of scope

- Any `src/` production code
- Scaffolding folders
- Tests, TTS calls, CLI

### Acceptance criteria

- [ ] Reviewer and implementer agree on UI → Service → Provider → External
- [ ] Agreed MVP packages: config, models, providers, services, ui (no controllers/app/utils by default)
- [ ] `docs/DECISIONS.md` exists with template fields and initial entries for no-Controller, no-`src/app`, and simplified flow
- [ ] Explicit approval recorded to proceed to Phase 1
- [ ] No production code written in this phase

### Manual test steps

1. Read Overview + this phase summary aloud or in review; confirm no Controller/`src/app` assumptions remain.
2. Open `docs/DECISIONS.md`; confirm seeded decisions are accurate.
3. Confirm Phase 1 will not create `src/controllers/`, `src/app/`, or empty `src/utils/`.

### Suggested unit tests

- None (docs/review only).

---

## Phase 1 — Project scaffolding

### Goal

Establish the package layout, dependency pin, and README skeleton so later layers have a stable home — **without** calling Edge TTS yet, and **without** Controllers, `src/app/`, or a preemptively empty `src/utils/`.

### Scope / what to build

- Create `src/` package tree with empty `__init__.py` for: `config`, `models`, `providers`, `services`, `ui`.
- Create `output/.gitkeep`, `assets/.gitkeep`, `tests/` placeholder.
- Pin `edge-tts` in `requirements.txt`.
- Add a minimal README (install, run, project purpose).
- Do **not** create `src/controllers/`, `src/app/`, or `src/utils/`.
- Do **not** invent `src/utils/logging_setup.py`; logging will be configured in `main.py` in Phase 7 (and polished in Phase 8).
- Leave `main.py` as a temporary stub or a no-op entry that only proves the package imports; do not keep production TTS calls in `main.py` beyond this phase’s temporary check.
- If any scaffolding decision differs from Architecture folder lists, append a short note to `docs/DECISIONS.md` (do not rewrite Architecture here).

### Files to create

- `src/__init__.py`
- `src/config/__init__.py`
- `src/models/__init__.py`
- `src/providers/__init__.py`
- `src/services/__init__.py`
- `src/ui/__init__.py`
- `output/.gitkeep`
- `assets/.gitkeep`
- `tests/__init__.py` (optional)
- `README.md`

### Files to modify

- `requirements.txt` — add `edge-tts`
- `main.py` — strip hardcoded TTS demo or reduce to import smoke only (full wiring is Phase 7)
- `docs/DECISIONS.md` — only if a scaffolding decision needs recording

### Explicitly out of scope

- Models, config loader, provider, service, CLI prompts
- Controllers, `src/app/`, `src/utils/`
- Real TTS generation
- Tests beyond “imports succeed”
- GUI

### Acceptance criteria

- [ ] `src/` contains only agreed MVP packages (config, models, providers, services, ui)
- [ ] No `src/controllers/`, `src/app/`, or empty `src/utils/` created
- [ ] `output/` and `assets/` exist and are tracked via `.gitkeep` (or equivalent)
- [ ] `requirements.txt` lists `edge-tts`
- [ ] `README.md` describes install and intended CLI usage at a high level
- [ ] No production `print()`-based status path introduced
- [ ] Package import smoke succeeds

### Manual test steps

1. Create/activate `.venv` and run `pip install -r requirements.txt`.
2. From project root, run `python -c "import src"` (or equivalent) and confirm no import errors.
3. Confirm folders `src/`, `output/`, `assets/`, `tests/` exist; confirm absence of `controllers/`, `app/`, `utils/` under `src/`.
4. Confirm `README.md` opens and is readable.

### Suggested unit tests

- None required (structure-only phase).

---

## Phase 2 — Models (pure data)

### Goal

Define typed dataclasses for voice configuration and generation request/result with **no** IO, network, or UI.

### Scope / what to build

- `Voice` — fields aligned with `voices.json` (`id`, `name`, `gender`, `language`).
- `GenerationRequest` — text, selected gender (or voice key), output filename (basename only).
- `GenerationResult` — success flag, output path, optional error message / error kind.
- Prefer a **single** `generation.py` module if small; split only if clarity demands it.
- Keep models free of validation that requires filesystem or network (light structural checks only if they stay pure).

### Files to create

- `src/models/voice.py`
- `src/models/generation.py`
- Update `src/models/__init__.py` exports if useful

### Files to modify

- None outside `src/models/` unless re-exporting from `__init__.py`

### Explicitly out of scope

- Reading `voices.json`
- Calling `edge-tts`
- Path resolution under `output/`
- CLI / service

### Acceptance criteria

- [ ] Models are `@dataclass` (or equivalent) with type hints
- [ ] No file IO, network, logging side effects, or UI imports in models
- [ ] Fields are sufficient for Male/Female voice config and a single generation round-trip
- [ ] Modules stay small and focused (prefer one `generation.py`)

### Manual test steps

1. In a short REPL or throwaway snippet, instantiate `Voice`, `GenerationRequest`, and `GenerationResult`.
2. Confirm instances hold expected field values.
3. Grep/models review: no `open`, `pathlib` write, `edge_tts`, or UI imports.

### Suggested unit tests

- Unit tests that construct `Voice`, `GenerationRequest`, and `GenerationResult` with typical field values and assert attributes round-trip.
- Add under `tests/` when convenient in this phase (or no later than Phase 9 gap-fill); do not defer “thinking” about them.

---

## Phase 3 — Config loader

### Goal

Load and validate `config/voices.json` into typed `Voice` models; fail clearly on invalid config.

### Scope / what to build

- Read-only config loader under `src/config/`.
- Parse JSON, validate required fields, return `list[Voice]` (or a small container type).
- Resolve config path relative to project root via `pathlib` (no hardcoded absolute paths).
- Raise meaningful exceptions for missing file, invalid JSON, missing voices, or incomplete entries (keep exceptions in the config module unless a second consumer clearly needs a shared type).
- Do **not** hardcode `uz-UZ-SardorNeural` / `uz-UZ-MadinaNeural` in business logic elsewhere; this layer surfaces whatever is in the file.

### Files to create

- `src/config/voices.py` (loader + validation)

### Files to modify

- `src/config/__init__.py` — export public loader API if appropriate
- `config/voices.json` — only if validation reveals format fixes; prefer leaving as-is if already valid
- `docs/DECISIONS.md` — only if a non-obvious path-resolution choice is made

### Explicitly out of scope

- TTS calls
- Output path validation for user filenames
- CLI
- Caching frameworks or settings.json
- Separate `exceptions.py` unless clearly needed

### Acceptance criteria

- [ ] Loader returns typed `Voice` instances matching JSON
- [ ] Male and Female entries from existing `voices.json` load successfully
- [ ] Invalid/missing config raises a clear exception (not a silent empty list without signal)
- [ ] Config module does not import services, providers, or UI
- [ ] No voice IDs hardcoded in services as a substitute for config

### Manual test steps

1. Call the loader against the real `config/voices.json`; confirm two voices with expected genders.
2. Temporarily point at a missing file path; confirm a clear error.
3. Temporarily break JSON syntax in a copy; confirm a clear error.
4. Restore original `voices.json`.

### Suggested unit tests

- Load a temp fixture JSON with Male/Female → assert two `Voice` instances and genders.
- Reject empty `voices` array / missing required fields with a clear exception.
- Reject invalid JSON / missing file with a clear exception.
- Prefer adding these in this phase (fixtures under `tests/`); pytest runner may land in Phase 9 if not already present.

---

## Phase 4 — Edge TTS provider (thin)

### Goal

Provide a thin async wrapper around `edge_tts` that synthesizes speech for given text + voice id and writes/returns audio — **no** UI, config parsing, or app orchestration.

### Scope / what to build

- `src/providers/edge_tts_provider.py` with an **async function** (prefer function over class unless a class adds clear value) such as: synthesize text with a voice id to a given `pathlib.Path`.
- Prefer writing via the path passed in by the caller (service owns output policy).
- Map/wrap library failures into meaningful exceptions; do not swallow errors.
- Log at DEBUG/INFO around the call boundaries without printing.
- No Provider Interface / ABC.

### Files to create

- `src/providers/edge_tts_provider.py`

### Files to modify

- `src/providers/__init__.py` — export public function if useful

### Explicitly out of scope

- Reading `voices.json`
- Empty-text / filename business rules (service layer)
- Provider Interface / ABC / DI
- CLI status messages
- Rate, pitch, volume parameters

### Acceptance criteria

- [ ] Async API using `async`/`await`
- [ ] Uses `edge_tts` only as external integration
- [ ] No UI or config-parsing imports
- [ ] Given valid text, voice id, and writable path, produces a non-empty MP3 (manual verification)
- [ ] Failures raise meaningful exceptions

### Manual test steps

1. From a small temporary async runner (not final CLI), call the provider with Madina voice id and a path under `output/` (e.g. `output/phase4_provider.mp3`).
2. Confirm the MP3 file exists and plays/is non-zero size.
3. Disconnect network or use an invalid voice id; confirm a raised error (not a hang without feedback).
4. Delete temporary test artifacts when done.

### Suggested unit tests

- Unit test with **mocked** `edge_tts` (or mocked communicate/save) asserting the provider is invoked with expected text/voice/path and that failures propagate.
- Live network tests remain manual only for MVP.
- Prefer adding the mock test in this phase; otherwise ensure it is listed for Phase 9 gap-fill.

---

## Phase 5 — Audio / generation service

### Goal

Implement business logic: validate request rules, resolve voice from config by gender, ensure output path stays under `output/`, call provider, return `GenerationResult`. This is the API the **CLI calls directly** (no Controller).

### Scope / what to build

- `src/services/audio_service.py` (name may be `generation_service.py` if clearer).
- Validate non-empty text.
- Validate filename (basename only; reject path separators, empty name, unsafe characters as needed for Windows).
- Resolve Male/Female → `Voice.id` via loaded config (not hardcoded IDs).
- Ensure final path is under project `output/` using `pathlib` (prevent path traversal); **keep path validation private in the service** (do not create `utils/paths.py`).
- Call Edge TTS provider; handle save permission failures.
- Return structured `GenerationResult`; raise or return errors consistently (choose one thin pattern for the UI).
- Logging at INFO/ERROR for generation start/success/failure.

### Files to create

- `src/services/audio_service.py` (or `generation_service.py`)

### Files to modify

- `src/services/__init__.py`
- `docs/DECISIONS.md` — if the raise-vs-result error pattern is a lasting choice worth recording

### Explicitly out of scope

- CLI prompts
- Controllers
- Provider Interface
- Batch generation
- Shared utils for paths

### Acceptance criteria

- [ ] Empty text is rejected with a clear domain error
- [ ] Invalid filename (e.g. `../secret`, empty, separators) is rejected
- [ ] Valid request writes MP3 under `output/` only
- [ ] Voice resolution uses config data
- [ ] Service does not import UI
- [ ] Service calls provider; does not embed raw `edge_tts.Communicate` if provider already exists
- [ ] No Controller layer introduced

### Manual test steps

1. Invoke service with valid Uzbek text, Female, filename `hello.mp3` → file at `output/hello.mp3`.
2. Empty text → readable error.
3. Filename `..\evil.mp3` or `foo/bar.mp3` → rejected.
4. Confirm Male resolves to Sardor id via config (inspect logs or result metadata if exposed).

### Suggested unit tests

- Filename / path-traversal rejection cases (unit, no network).
- Empty text rejection.
- Service with **mocked** provider: valid request returns success/`GenerationResult` without calling real Edge TTS; voice resolved from fixture config.
- Prefer landing these tests in this phase.

---

## Phase 6 — CLI UI (presentation)

### Goal

Implement CLI interaction under `src/ui/`: prompt for text, voice (Male/Female), filename; show status; display user-friendly errors. CLI must **never** generate audio directly — it calls the **service** only.

### Scope / what to build

- `src/ui/cli.py` (or `src/ui/cli_app.py`) that:
  - Prompts for Uzbek text
  - Prompts for Male/Female
  - Prompts for output filename
  - Shows “generating…” / success / failure status
  - Maps domain/provider errors to readable messages (empty text, invalid filename, network unavailable, Edge TTS failure, save permission failure)
- Call **service** only; no provider bypass; **no Controller**.
- Use logging for diagnostics; user-visible status may use stdout carefully — keep presentation-only echoes in the UI layer (PRD FR-06). Prefer inline strings in the UI module; add `messages.py` only if clutter clearly warrants it.

### Files to create

- `src/ui/cli.py`

### Files to modify

- `src/ui/__init__.py`

### Explicitly out of scope

- GUI frameworks
- Controllers
- `main.py` final wiring (next phase)
- Changing service/provider APIs unless a blocker is found (then stop and ask)
- Optional `messages.py` unless needed for clarity

### Acceptance criteria

- [ ] User can enter text, select Male/Female, choose filename (PRD FR-01–FR-03)
- [ ] Status is displayed during/after generation (FR-06)
- [ ] Errors show readable messages; no unexpected crash on known failure modes (FR-07 / PRD §11)
- [ ] UI does not import or call `edge_tts` / provider directly
- [ ] Happy path produces MP3 under `output/` via **UI → Service → Provider**

### Manual test steps

1. Run the CLI entry (temporary harness or early `main` if already wired) with sample Uzbek text, Female, `cli_test.mp3`.
2. Listen/confirm file exists and is understandable.
3. Submit empty text; confirm friendly message.
4. Submit invalid filename; confirm friendly message.
5. (Optional) Disable network and retry; confirm friendly network/TTS failure message.

### Suggested unit tests

- None required for interactive CLI in MVP; optional later with stdin redirection. Prefer not inventing UI automation for MVP.

---

## Phase 7 — `main.py` entrypoint wiring

### Goal

Wire the real application entrypoint: configure logging in `main.py`, start the CLI, and remove the old hardcoded TTS stub. No `src/app/` bootstrap package.

### Scope / what to build

- Replace stub `main.py` with: logging setup (stdlib `logging` in `main.py`) → run CLI (async via `asyncio.run` as needed).
- Ensure running `python main.py` from project root starts the MVP flow.
- Confirm `requirements.txt` remains accurate (`edge-tts` only as runtime dep).
- Do **not** create `src/app/` or `logging_setup.py` unless a second independent module already needs the same helper (YAGNI — it should not for MVP).

### Files to create

- None required

### Files to modify

- `main.py` — full wiring; remove hardcoded `TEXT` / `VOICE` / `OUTPUT` demo; configure logging here
- `README.md` — exact run instructions (`python main.py`)
- `requirements.txt` — verify `edge-tts` pin/name

### Explicitly out of scope

- New features
- GUI
- `src/app/`, Controllers, utils extraction for logging
- Extra CLI flags beyond the interactive flow (unless already approved)

### Acceptance criteria

- [ ] `python main.py` launches the interactive CLI
- [ ] End-to-end generation works from the entrypoint
- [ ] No leftover stub constants driving TTS in `main.py`
- [ ] Logging is initialized in `main.py` before generation
- [ ] No `src/app/` package introduced

### Manual test steps

1. From project root with venv active: `python main.py`.
2. Complete one Male and one Female generation.
3. Confirm files land in `output/` and logging shows INFO-level progress without relying on debug spam.

### Suggested unit tests

- None (smoke is manual).

---

## Phase 8 — Error handling and logging polish

### Goal

Harden coverage of PRD §11 error cases and logging levels so failures are consistent, user-friendly in the UI, and diagnosable in logs.

### Scope / what to build

- Audit empty text, invalid filename, network unavailable, Edge TTS failure, save permission failure end-to-end through **UI → Service → Provider**.
- Ensure exceptions are meaningful near the source; UI maps them to readable messages; nothing is swallowed.
- Tune log levels: INFO for normal flow, WARNING/ERROR for failures, DEBUG for detail (logging configured from `main.py`).
- Remove any remaining development `print()` from non-UI production paths.

### Files to create

- Only if a small shared type is still missing and clearly helps **two** modules; otherwise modify existing modules only

### Files to modify

- `src/services/*`, `src/providers/*`, `src/ui/cli.py`, `main.py` (logging config) as needed
- `README.md` — brief troubleshooting note optional
- `docs/DECISIONS.md` — if error-handling pattern is finalized as a lasting decision

### Explicitly out of scope

- New product features
- Controllers / `src/app/`
- Telemetry/cloud logging
- Inventing utils solely for logging polish

### Acceptance criteria

- [ ] Empty text → friendly UI message + appropriate log
- [ ] Invalid filename → friendly UI message + appropriate log
- [ ] Network unavailable → friendly UI message (no raw undecorated traceback as the only UX)
- [ ] Edge TTS failure → friendly UI message
- [ ] Save permission failure → friendly UI message (simulate by targeting a non-writable scenario if feasible on Windows)
- [ ] Application does not crash unexpectedly on these cases
- [ ] Production paths avoid `print()` outside deliberate UI presentation

### Manual test steps

1. Exercise each PRD §11 case once from the CLI.
2. Confirm logs contain enough context (error type/message) without dumping secrets (N/A for this app).
3. Confirm success path still works after polish.

### Suggested unit tests

- Ensure validation-error unit tests from Phases 3 and 5 still pass; add any missing cases discovered during polish.

---

## Phase 9 — Test consolidation (pytest harness + gap fill)

### Goal

Add a light pytest harness and fill any remaining unit-test gaps — **not** a deferred dump of all testing. Most meaningful unit tests should already exist from Phases 2–5.

### Scope / what to build

- Add `pytest` via `requirements-dev.txt` (keep runtime `requirements.txt` to `edge-tts` only).
- Ensure `pytest` runs from project root.
- Fill gaps only if earlier phases missed suggested tests:
  - Config loader fixtures
  - Model construction smoke
  - Filename / output-path validation
  - Service with mocked provider
  - Provider with mocked `edge_tts` (optional if already present)
- Do not require live Edge TTS in unit tests for MVP.
- Document how to run tests in README.

### Files to create

- `requirements-dev.txt` containing `pytest`
- Any missing `tests/test_*.py` files needed to close gaps (e.g. `test_voices_config.py`, `test_path_validation.py`, `test_audio_service.py`)

### Files to modify

- `README.md` — how to run tests
- Possibly service/provider seams for testability **without** introducing a formal Provider Interface (e.g. pass an async callable / optional dependency parameter only if needed and kept minimal)
- `docs/DECISIONS.md` — only if a testability seam is a lasting architectural choice

### Explicitly out of scope

- Full end-to-end live TTS suite
- UI automation
- Coverage gates / complex CI
- Rewriting earlier phases’ logic solely to force interfaces

### Acceptance criteria

- [ ] `pytest` runs from project root and passes
- [ ] Config tests cover happy path + at least one invalid config
- [ ] Path/filename tests cover rejection of traversal/unsafe names
- [ ] Service test does not call the real network
- [ ] No new layers (Controller/DI/Provider Interface) introduced for testability
- [ ] Gaps from Phases 2–5 suggested tests are closed or explicitly waived with reviewer approval

### Manual test steps

1. `pip install -r requirements-dev.txt`.
2. Run `pytest`.
3. Confirm failures are readable when breaking a fixture on purpose, then restore.

### Suggested unit tests

- This phase consolidates/fills gaps; it is not the first time tests are considered.

---

## Phase 10 — MVP acceptance / smoke checklist

### Goal

Verify the product against PRD §15 and close the MVP as complete.

### Scope / what to build

- No new features. Perform the acceptance checklist; fix only blockers found (each fix should be a small, approved follow-up if non-trivial).
- Update README if any run steps drifted.
- Confirm code remains clean: **UI → Service → Provider**, no Controllers/`src/app/`/empty utils, `docs/DECISIONS.md` maintained for decisions made during implementation.

### Files to create

- None expected

### Files to modify

- Only blocker fixes or README accuracy tweaks; append to `docs/DECISIONS.md` if a last-minute decision was required

### Explicitly out of scope

- GUI, batch, CSV, TXT import, voice settings (rate/pitch/volume), multi-language, cloud, auth, database
- Rewriting Architecture docs (separate approved docs task if needed)

### Acceptance criteria (PRD §15)

- [ ] User enters Uzbek text
- [ ] User selects Male or Female voice
- [ ] Application generates MP3 successfully
- [ ] Audio is understandable
- [ ] MP3 is saved correctly under `output/`
- [ ] Errors are handled gracefully
- [ ] Code is clean and maintainable (simplified layers respected; no premature abstractions; logging in place; voices from config; no Controllers)
- [ ] `docs/DECISIONS.md` reflects MVP architectural decisions made during the project

### Manual test steps (smoke)

1. Fresh venv: install `requirements.txt`, run `python main.py`.
2. Generate Female sample; play file.
3. Generate Male sample; play file.
4. Re-test empty text and invalid filename briefly.
5. Spot-check project structure: `config`, `models`, `providers`, `services`, `ui` present; no `controllers/` or `app/`.
6. Run `pytest` (Phase 9 harness).

### Suggested unit tests

- None new; rely on Phase 9 suite + earlier phase tests + manual smoke.

---

## Final MVP definition of done

The MVP is **done** when Phases 0–10 are complete and approved, and all of the following hold:

1. CLI flow matches PRD user flow (§7) and functional requirements FR-01–FR-07.
2. Voices come from `config/voices.json` (Male/Female Uzbek neural voices).
3. MP3 files are written only under `output/`.
4. PRD §11 errors are handled with readable UI messages and logging.
5. Code follows the simplified stack **UI → Service → Provider → External** and Cursor Rules (type hints, pathlib, dataclass, async/await, small functions); **no Controllers**, no `src/app/`, no empty `utils/` dumping ground.
6. `docs/DECISIONS.md` is present and updated for architectural/technical decisions made during implementation.
7. No GUI, batch, CSV, subtitles, translation, cloud, auth, or database.
8. Runtime dependency remains `edge-tts` (+ transitive); tests use `pytest` as a dev dependency.
9. `python main.py` is the supported entrypoint; README documents install and use.

---

## Future work (post-MVP)

Not phased for implementation now. Tracked for later versions per PRD §14 / Architecture §12:

| Version / theme | Items |
| --- | --- |
| 1.1 | Desktop GUI (`src/ui/`), **same service → provider stack** (no Controller required) |
| 1.2 | Batch generation |
| 1.3 | TXT import |
| 1.4 | CSV import |
| 1.5 | Voice settings (rate, pitch, volume) |
| 2.0 | Multi-language (Indonesian, English, Japanese, Arabic) |
| Architecture (when justified) | Provider Interface, DI, additional TTS providers, audio preview |

Do **not** start these until MVP is accepted and a new plan is approved.

---

## Implementation gate (MVP)

> **Stop here until this plan is reviewed and approved.**  
> **Also complete and approve Phase 0 (Architecture Validation)** — including `docs/DECISIONS.md` initial entries — **before any production coding (Phase 1+).**  
> After approval, implement **one phase at a time**, explain changes, and wait for review before continuing — per `cursor_rules.md` workflow.

---

## Phase 2 — GUI Development (Post-MVP)

| Field | Value |
| --- | --- |
| **Track** | Post-MVP / Phase 2 GUI |
| **Status** | Complete (G0–G10) |
| **Depends on** | MVP Phases 0–10 complete (CLI + CSV batch live) |
| **UI toolkit** | CustomTkinter ([ADR-010](DECISIONS.md)) |
| **Shared engine** | Existing `src/services/` + providers ([ADR-011](DECISIONS.md)) — not a new `core/` package |
| **CLI** | Retained; not replaced |

> Note: MVP **Phase 2 — Models** above is historical and complete. This section is the separate **product Phase 2 (GUI)** roadmap. Implement GUI milestones one at a time; wait for approval between milestones per Cursor Rules.

### Goals

- Windows desktop native GUI for single-text and CSV batch generation.
- Non-technical users can generate audio without the CLI; setup ideally under ~5 minutes via `.exe`.
- No UI freeze during batch; preview before final use; output folder management.
- No speed/pitch controls (Edge TTS Uzbek constraint).

### Milestone checklist

- [x] **G0 — Align & decide** — ADR-010/ADR-011 confirmed. Entrypoint: `gui_main.py` and `python main.py --gui` (both launch the same GUI).
- [x] **G1 — Shared-path audit** — CLI/`batch_csv` call `generate_audio` only (no Edge TTS in UI). Shared friendly `message_for` extracted to `src/ui/messages.py` (G4); batch progress callbacks still `print` only until G6; avoid private `_validate_output_subdir` import long-term. No parallel `core/` package.
- [x] **G2 — GUI skeleton** — CustomTkinter window with clear areas/tabs for **Single text** and **Batch CSV**; empty actions wired to placeholders; no Edge TTS imports in GUI modules.
- [x] **G3 — Voice selection** — Male/Female dropdown bound to `config/voices.json` (same voices as CLI).
- [x] **G4 — Single-text generate** — Call `generate_audio` from a worker; show success/failure via friendly dialogs; write under `output/` with existing `.mp3` rules. Done: `GenerateWorker` in `src/ui/gui/workers.py`; CLI+GUI share `src/ui/messages.py`; busy-state + `tkinter.messagebox`; flat `output/` (no `output_subdir`).
- [x] **G5 — Audio preview / play** — Play generated MP3 before user finishes the flow; playback must not freeze the UI; justify any new dependency. Done: `os.startfile` Play (ADR-012); `_last_output_path`; no new deps.
- [x] **G6 — CSV batch + progress** — File picker; reuse/extend batch CSV flow; progress bar + queue; worker thread/async bridge; row-level OK/FAIL; continue after row errors; respect batch output subfolder policy. Done: `BatchProgressEvent` + optional `report` in `batch_csv.py`; `BatchWorker`; Browse/Run/progress/log; cross-tab busy.
- [x] **G7 — Output / download management** — Show/open output folder; surface auto-rename / `.mp3` normalization; batch folder `output/<csv_stem>/` parity with CLI. Done: `get_output_dir()`; Open folder (single/batch); `.mp3` normalized status note (ADR-013).
- [x] **G8 — Manual testing** — Single text; batch CSV; corrupt/missing CSV; empty text; invalid filename; network/TTS failure; save permission; UI remains responsive under batch. Done: `docs/manual_testing_gui.md` (MT-01…MT-16 + CLI smoke Pass).
- [x] **G9 — Package `.exe`** — PyInstaller (or approved equivalent) for Windows; test on a clean Windows machine without a pre-existing venv workflow; document size and antivirus false-positive notes if any. Done: ADR-014; frozen paths; `uzbek_tts_gui.spec`; `docs/packaging.md` (~14.1 MB onefile; clean-folder smoke).
- [x] **G10 — Docs & promo** — Update README (GUI install + screenshots); add demo GIF; push GitHub-ready materials; prepare short Threads promo copy pointing at the `.exe`/release. Done: README GUI-first; `assets/screenshots/` + `assets/demo.gif`; `docs/promo_threads.md`; packaging release notes.

### Explicitly out of scope (this track)

- Speed / pitch / synthesis volume controls
- Web/Gradio UI
- Removing CLI
- Controllers / `src/app/` / parallel `src/core/` TTS engine
- Cloud hosting, auth, database

### Definition of done (GUI Phase 2)

1. Non-technical happy path works for single text and CSV batch in the GUI.
2. CLI interactive and `--csv` still pass smoke checks.
3. No duplicated Edge TTS or filename/voice rules in GUI code.
4. Packaged Windows build documented and smoke-tested on clean Windows.
5. README + visual demo assets ready for public GitHub / Threads distribution.

---

## Implementation gate (GUI)

> Phase 2 GUI milestones G0–G10 are complete. Further GUI work needs a new approved plan / ADR.

---

*End of Implementation Plan v1.1 (+ Phase 2 GUI appendix)*
