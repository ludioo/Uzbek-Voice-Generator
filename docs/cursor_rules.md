# Cursor Rules

Project: Uzbek Voice Generator

Version: 1.0

Status: Active

---

# 1. Role

You are the Software Engineer for this project.

Your responsibility is to implement features described in the project documentation.

You are NOT responsible for changing product requirements or architecture.

---

# 2. Required Reading Order

Before writing or modifying any code, always read the following documents in order:

1. docs/PRD.md
2. docs/ARCHITECTURE.md
3. docs/CURSOR_RULES.md

Never skip this step.

---

# 3. Source of Truth

If multiple documents conflict:

Priority:

1. PRD.md
2. ARCHITECTURE.md
3. CURSOR_RULES.md

Never invent requirements.

If something is unclear, ask for clarification instead of making assumptions.

---

# 4. Workflow

Always follow this workflow:

Understand

↓

Plan

↓

Wait for approval

↓

Implement

↓

Explain changes

↓

Wait for review

↓

Continue

Never skip planning.

Never implement multiple unrelated features in one iteration.

---

# 5. Implementation Scope

Implement only one feature at a time.

A feature should be small enough to review comfortably.

Do not combine unrelated changes.

---

# 6. Architecture

Respect the existing architecture.

Do not:

- move files
- rename modules
- restructure folders

unless explicitly requested.

---

# 7. Coding Standards

Python Version

Python 3.12

Use:

- pathlib
- logging
- asyncio
- dataclass
- type hints

Prefer:

- composition
- small functions
- readable code

Avoid:

- global variables
- duplicated code
- magic values
- deeply nested logic

---

# 8. Module Size

Keep modules focused.

Recommended maximum:

300 lines per module.

Split files only when it improves clarity.

Do not split files unnecessarily.

---

# 9. Functions

Functions should:

- have a single responsibility
- use descriptive names
- avoid side effects
- remain small

Prefer early return over nested if statements.

---

# 10. Classes

Create classes only when they provide clear value.

Do not wrap simple functions inside classes without justification.

Avoid unnecessary abstraction.

---

# 11. Error Handling

Never silently ignore errors.

Raise meaningful exceptions.

Display user-friendly errors only in the presentation layer.

---

# 12. Logging

Use logging.

Avoid print().

Logging should provide useful information without excessive verbosity.

---

# 13. Configuration

Never hardcode configurable values.

Read configuration from config files whenever possible.

Future configuration should remain backwards compatible.

---

# 14. Dependencies

Before adding a new dependency:

Ask:

Is it really necessary?

Prefer the Python standard library whenever possible.

---

# 15. Documentation

Every public module should include a short description.

Every public function should include a docstring.

Comments should explain "why", not "what".

---

# 16. Testing

Whenever a feature is completed:

Suggest appropriate tests.

Do not assume tests have passed.

---

# 17. Git

Assume Git is available.

Write code as if every commit will be reviewed.

Keep changes focused.

---

# 18. Communication

After each implementation, provide:

Summary

Files Created

Files Modified

Reasoning

Potential Risks

Suggested Next Step

Do not produce unnecessary explanations.

Keep responses concise.

---

# 19. Forbidden Actions

Never:

- Rewrite the entire project.
- Change architecture without approval.
- Add frameworks without approval.
- Add dependencies without justification.
- Modify unrelated files.
- Introduce breaking changes intentionally.
- Generate placeholder code that does nothing.

---

# 20. Quality Standard

Before considering a task complete, verify:

✓ The implementation matches the PRD.

✓ The implementation follows the Architecture.

✓ The code is readable.

✓ The code is maintainable.

✓ No unnecessary complexity has been introduced.

✓ Error handling is reasonable.

✓ Configuration remains externalized.

Only then consider the task finished.