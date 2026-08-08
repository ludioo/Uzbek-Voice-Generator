# PRD - Uzbek Voice Generator

Version: 1.0
Status: MVP + Phase 2 GUI complete
Author: ChatGPT
Target Platform: Windows
Language: Python 3.12

---

# 1. Overview

Uzbek Voice Generator is a lightweight desktop application that converts Uzbek text into speech using Microsoft Edge TTS.

The application is designed to generate individual MP3 audio files using high quality Uzbek neural voices.

Primary goal is simplicity, reliability, and maintainability.

This project is intended for personal production workflow and is not intended to become a commercial SaaS.

---

# 2. Goals

The application must:

- Generate Uzbek speech.
- Support both Male and Female voices.
- Export MP3 audio.
- Be easy to use.
- Be easy to maintain.
- Be easy to extend in the future.

---

# 3. Non Goals

The MVP will NOT support:

- Voice cloning
- AI voice generation
- Voice training
- Batch CSV import
- Subtitle generation
- Translation
- Cloud storage
- Online editor
- Authentication
- Database

These may be added in future versions.

---

# 4. Supported Voices

Current voices:

Male

- uz-UZ-SardorNeural

Female

- uz-UZ-MadinaNeural

The application architecture must allow adding more voices in the future.

---

# 5. Target Users

Primary user:

Solo content creator

Technical level:

Basic Python knowledge.

---

# 6. Functional Requirements

## FR-01

User can enter Uzbek text.

---

## FR-02

User can select voice.

Available options:

- Male
- Female

---

## FR-03

User can choose output filename.

---

## FR-04

Application generates MP3.

---

## FR-05

Generated audio is saved inside output folder.

---

## FR-06

Application displays generation status.

---

## FR-07

Application handles generation errors gracefully.

---

# 7. User Flow

Start Application

↓

Enter Uzbek Text

↓

Choose Voice

↓

Choose Output Filename

↓

Click Generate

↓

Generate Audio

↓

Save MP3

↓

Done

---

# 8. Folder Structure

project/

    src/

    output/

    assets/

    tests/

    main.py

    requirements.txt

    README.md

---

# 9. Technical Stack

Python 3.12

Edge TTS

asyncio

pathlib

logging

No external database.

No web server.

No API backend.

---

# 10. UI

MVP can be CLI.

GUI will be added later.

Current priority:

Working generation pipeline.

---

# 11. Error Handling

Application should handle:

- Empty text
- Invalid filename
- Network unavailable
- Edge TTS failure
- Save permission failure

Errors should display readable messages.

Never crash unexpectedly.

---

# 12. Logging

Use Python logging module.

Avoid print() except during development.

---

# 13. Coding Standards

Use:

- type hints
- pathlib
- dataclass where appropriate
- async / await
- small functions
- single responsibility principle

Avoid:

- global variables
- duplicated code
- magic strings
- hardcoded paths

---

# 14. Future Roadmap

Version 1.1

- GUI

Version 1.2

- Batch Generation

Version 1.3

- TXT Import

Version 1.4

- CSV Import

Version 1.5

- Voice Settings

- Rate

- Pitch

- Volume

Version 2.0

Multi-language support

- Indonesian

- English

- Japanese

- Arabic

---

# 15. Acceptance Criteria

The MVP is considered complete when:

✓ User enters Uzbek text.

✓ User selects Male or Female voice.

✓ Application generates MP3 successfully.

✓ Audio is understandable.

✓ MP3 is saved correctly.

✓ Errors are handled gracefully.

✓ Code is clean and maintainable.

---

# Phase 2 — GUI Development

Status: Complete (post-MVP; G0–G10 shipped)

CLI MVP (interactive + CSV batch) remains supported. Phase 2 adds a Windows desktop GUI for non-technical users while keeping the same generation pipeline. Packaged entry: `UzbekTTS.exe` (PyInstaller onefile; see `docs/packaging.md`). Dev entries: `gui_main.py` / `python main.py --gui`.

## Why GUI next

The CLI satisfies power users and automation. Public distribution (GitHub + Threads) needs a path where people who do not use terminals can still generate Uzbek speech. A native Windows GUI is the next product step toward a single `.exe` install.

## Target users

- General public discovering the project on GitHub or Threads
- Non-technical content creators who need Male/Female Uzbek MP3s quickly
- Existing CLI users who optionally prefer a visual batch workflow

Technical level for Phase 2 success: no Python or terminal knowledge required for the packaged app.

## Goals

- Ship a Windows desktop native GUI (not a web app).
- Let a non-technical user generate single-text and CSV-batch audio without the CLI.
- Keep install/setup under about 5 minutes (ideally one `.exe` via PyInstaller).
- Reuse the existing Service → Provider stack; do not duplicate Edge TTS or validation logic in UI code.
- Retain the CLI for power users and automation.

## Success criteria

- A first-time Windows user can generate a Male or Female MP3 from typed text using only the GUI.
- The same user can upload a UTF-8 CSV, see progress, and receive files under the managed output folder.
- UI stays responsive during batch (progress bar + queue; TTS work off the main UI thread).
- User can preview/play generated audio before treating it as final.
- Setup for the packaged build is documented and typically under 5 minutes.
- CLI interactive and `--csv` modes still work after GUI work lands.

## Mandatory features

- Manual text input (single generation)
- Upload and process CSV (batch), consistent with existing CSV columns (`text`, `gender`, `filename`)
- Voice select: Male / Female dropdown (Uzbek Edge TTS voices from config)
- Preview / play generated audio before save (or before closing the result flow)
- Progress bar and queue for CSV batch; no UI freeze
- Output / download management (output folder, auto `.mp3` rename / normalization, batch subfolder policy aligned with CLI)
- Friendly error dialogs for empty text, invalid files, network/TTS failure, and save permission issues

## Out of scope (Phase 2)

- Speed / rate controls
- Pitch controls
- Volume as a synthesis parameter (Edge TTS Uzbek model limitation for this product — treat as a documented constraint, not a defect)
- Cloud hosting, SaaS, authentication, or online editor
- Voice cloning, training, or non–Edge TTS providers
- Replacing or removing the CLI
- Web UI / Gradio / browser-based apps

## Constraint note

Edge TTS Uzbek voices used by this project do not expose reliable productized speed/pitch controls for this app. Phase 2 must not advertise or implement those controls.
