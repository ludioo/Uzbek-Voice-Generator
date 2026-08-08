# Architecture Document

Project: Uzbek Voice Generator

Version: 1.0

Status: Active (MVP + Phase 2 GUI)

---

# 1. Architecture Goals

This project follows a modular and layered architecture.

The primary objectives are:

- Keep the codebase simple.
- Separate responsibilities clearly.
- Minimize coupling between modules.
- Make future features easy to implement.
- Allow replacing the TTS provider without affecting the rest of the application.

This project prioritizes maintainability over premature optimization.

---

# 2. Design Principles

The project follows these engineering principles:

- Single Responsibility Principle
- Separation of Concerns
- Composition over Inheritance
- Explicit is better than implicit
- Readability over cleverness
- Small modules over large modules
- Configuration over hardcoded values

---

# 3. High-Level Architecture

The application is divided into independent layers.

```text
Presentation Layer
        │
        ▼
Application Layer
        │
        ▼
Service Layer
        │
        ▼
Provider Layer
        │
        ▼
External Service
```

Responsibilities:

Presentation

- User interaction
- Input validation
- Display results

Application

- Coordinate application flow
- Connect presentation with services

Service

- Business logic
- Audio generation
- File creation

Provider

- Third-party integrations
- Edge TTS implementation

External

- Microsoft Edge TTS

---

# 4. Dependency Rules

Dependencies always flow downward.

Allowed:

Presentation
→ Application

Application
→ Services

Services
→ Providers

Providers
→ External APIs

Forbidden:

Providers importing UI

Services importing GUI

Configuration importing business logic

Circular imports

---

# 5. Project Structure

```text
project/

│
├── config/
│   └── voices.json
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── CURSOR_RULES.md
│   └── IMPLEMENTATION_PLAN.md
│
├── output/
│
├── assets/
│
├── tests/
│
├── src/
│
│   ├── app/
│   │
│   ├── config/
│   │
│   ├── controllers/
│   │
│   ├── models/
│   │
│   ├── providers/
│   │
│   ├── services/
│   │
│   ├── utils/
│   │
│   └── ui/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# 6. Layer Responsibilities

## Models

Contains pure data structures.

Rules:

- No business logic
- No file IO
- No network
- No UI

---

## Config

Responsible for reading project configuration.

Examples:

voices.json

future settings.json

Rules:

- Read only
- Validate configuration
- Return typed models

---

## Providers

Responsible for communicating with external libraries.

Current provider:

Edge TTS

Future providers:

Azure Speech

OpenAI

Local TTS

Rules:

- No UI
- No configuration parsing
- No application logic

---

## Services

Contains business logic.

Examples:

Generate audio

Prepare output

Manage generation

Services never communicate directly with the user interface.

---

## Controllers

Coordinate user actions.

Responsibilities:

Receive user requests

Call services

Return results

Controllers should remain thin.

---

## UI

Responsible only for user interaction.

Future implementations:

CLI

Desktop GUI

The UI should never generate audio directly.

---

# 7. Configuration Strategy

All configurable values must live outside the source code.

Examples:

voices.json

future settings.json

Avoid hardcoded values whenever possible.

---

# 8. Data Flow

```text
User

↓

Controller

↓

Service

↓

Provider

↓

Edge TTS

↓

MP3

↓

Output Folder
```

The data flow should always remain one directional.

---

# 9. Error Handling

Errors should be handled close to their source.

Rules:

- Raise meaningful exceptions
- Avoid silent failures
- Never swallow exceptions
- Display user-friendly messages in Presentation Layer

---

# 10. Logging Strategy

Use Python logging.

Avoid print() in production code.

Recommended log levels:

DEBUG

INFO

WARNING

ERROR

CRITICAL

---

# 11. Testing Strategy

Each layer should be testable independently.

Recommended:

Unit Tests

Configuration Tests

Provider Tests

Integration Tests

Avoid testing multiple layers together unless necessary.

---

# 12. Extensibility

The architecture should support future features without requiring major refactoring.

Planned future extensions:

GUI

Batch generation

CSV import

TXT import

Multi-language support

Additional TTS providers

Voice settings

Audio preview

---

# 13. Performance

Current project size is small.

Priorities:

Correctness

Maintainability

Readability

Performance optimization should only be introduced when supported by measurable evidence.

---

# 14. Security

No user authentication.

No database.

No sensitive data storage.

Avoid executing arbitrary user input.

Validate output paths before writing files.

---

# 15. Architecture Decision Record

Current Provider

Microsoft Edge TTS

Reason:

- High quality voices
- Supports Uzbek Male and Female
- Easy integration
- No API key required for this project
- Suitable for generating approximately 100 audio files

Future providers should be replaceable without modifying business logic.

---

# 16. Future Architecture

Future versions may introduce:

Provider Interface

Dependency Injection

Plugin-based providers

GUI Framework

Background task queue

These features should only be introduced when justified by project growth.

Premature abstraction should be avoided.

---

# Phase 2 — GUI Development

Status: Complete (post-MVP)

This section extends the MVP architecture for a Windows desktop GUI. It does **not** replace the layered model or the MVP simplification **UI → Service → Provider → External**. CLI and GUI are two presentation surfaces over the same service.

## Shared core (no logic duplication)

TTS calls, voice resolution, filename / path policy, `.mp3` normalization, and `GenerationResult` handling already live under `src/services/` and `src/providers/`. Phase 2 must **not** invent a parallel `core/tts_engine.py` that reimplements those rules.

| Surface | Location | Calls |
| --- | --- | --- |
| CLI | `src/ui/cli.py`, `src/ui/batch_csv.py` | `generate_audio` (service) |
| GUI | `src/ui/gui/` (or `src/ui/gui.py` if kept small) | same service APIs |

CSV parsing and batch orchestration may stay in a shared UI-adjacent module (reuse/extend `src/ui/batch_csv.py` or extract only presentation-free helpers) as long as synthesis still goes through the service. GUI files must never import `edge_tts` or call the provider directly.

## Target folder structure (post–Phase 2)

```text
project/
├── config/
│   └── voices.json
├── docs/
├── output/
├── assets/                 # icons, demo assets for GUI packaging
├── tests/
├── src/
│   ├── config/
│   ├── models/
│   ├── providers/          # Edge TTS only
│   ├── services/           # shared generation / path policy (CLI + GUI)
│   └── ui/
│       ├── cli.py
│       ├── batch_csv.py
│       ├── messages.py     # shared friendly GenerationResult copy (CLI + GUI)
│       └── gui/            # CustomTkinter presentation only
│           ├── app.py
│           ├── views/      # optional split when modules grow
│           └── workers.py  # background thread / async bridge
├── main.py                 # CLI entry (default)
├── gui_main.py             # GUI entry (or main.py --gui)
├── uzbek_tts_gui.spec      # PyInstaller onefile recipe (ADR-014)
├── requirements.txt
├── requirements-dev.txt    # pytest + PyInstaller
└── README.md
```

Related docs: `docs/packaging.md`, `docs/manual_testing_gui.md`, `docs/promo_threads.md`. Frozen builds read `config/voices.json` from `sys._MEIPASS` and write `output/` beside the `.exe` (ADR-014).

Do not add `src/controllers/` or `src/app/` for Phase 2 unless a new ADR says otherwise. Prefer thin GUI modules that call the service the same way the CLI does.

## Data flow (GUI)

```text
User (GUI)
    │
    ▼
Presentation (CustomTkinter)
    │  validate UI fields / file pickers
    ▼
Service (audio_service.generate_audio)
    │  voice from config, path policy, GenerationResult
    ▼
Provider (edge_tts_provider)
    │
    ▼
Microsoft Edge TTS
    │
    ▼
MP3 under output/  (or output/<csv_stem>/ for batch)
    │
    ▼
GUI preview player / save confirmation
```

CLI continues to use the identical downward path. No upward imports from services/providers into GUI.

## Threading model (prevent UI freeze)

Edge TTS work is async and network-bound. The GUI main thread must only paint widgets and handle events.

```text
Main UI thread
    │  enqueue job / update progress bar
    ▼
Worker thread (or asyncio loop on a dedicated thread)
    │  run generate_audio / batch rows
    ▼
Thread-safe callbacks / queue
    │  progress %, row status, errors, output paths
    ▼
Main UI thread
    │  refresh progress, dialogs, enable preview
```

Rules:

- Never call the service/provider synchronously on the main UI thread for generation or full CSV batches.
- Use a queue or equivalent so progress updates are marshalled back to the UI thread.
- Cancel/stop (if offered) must be cooperative and must not leave the UI deadlocked.
- Preview playback must not block the UI; if the player API is blocking, run it off the main thread or use a non-blocking API.

## How CLI and GUI share code

```text
                ┌─────────────┐
                │  config /   │
                │  models     │
                └──────┬──────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   src/ui/cli*                 src/ui/gui*
         │                           │
         └─────────────┬─────────────┘
                       ▼
              src/services/*
                       │
                       ▼
              src/providers/*
                       │
                       ▼
                 Edge TTS
```

Acceptance for architecture: any change to voice mapping, output naming, or TTS error mapping is made once in service/provider and automatically applies to both CLI and GUI. User-facing copy for known `error_kind` values lives in `src/ui/messages.py` (CLI + GUI); do not duplicate those strings in widgets.