# PRD - Uzbek Voice Generator

Version: 1.0
Status: MVP
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
