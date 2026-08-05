# Architecture Document

Project: Uzbek Voice Generator

Version: 1.0

Status: Draft

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