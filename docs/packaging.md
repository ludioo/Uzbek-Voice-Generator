# Packaging — Windows GUI `.exe` (G9)

Build a single-file Windows GUI binary with PyInstaller (ADR-014).

## Prerequisites

- Windows + Python 3.12
- Project venv with runtime + build deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Build

From the repository root:

```powershell
pyinstaller uzbek_tts_gui.spec
```

Artifact: `dist/UzbekTTS.exe` (onefile, no console window).

Do not commit `build/` or `dist/` (gitignored). Upload the exe via GitHub Releases.

## Frozen path behavior

| Kind | Location when frozen |
| --- | --- |
| `config/voices.json` | Inside bundle (`sys._MEIPASS/config/voices.json`) |
| `output/` | Beside the exe: `<exe_dir>/output/` |

Unfrozen (dev) layout is unchanged: project-root `config/` and `output/`.

## Local smoke (dev machine)

1. Run `dist\UzbekTTS.exe`.
2. Single text → Generate → Play → Open folder.
3. Batch → select `examples\sample_batch.csv` → Run → Open folder.
4. Confirm MP3s appear under `dist\output\` (or whatever folder contains the exe), **not** only under a temp extract path.

## Clean-machine smoke

1. Copy only `UzbekTTS.exe` (and optionally a sample CSV) to a Windows profile **without** this project’s venv.
2. Run MT-01 (single), MT-03 (Play), MT-06 (batch), MT-12 (offline / disconnect briefly) from [`docs/manual_testing_gui.md`](manual_testing_gui.md).
3. Record size and any Defender/SmartScreen prompts below.

## Size & antivirus notes

| Field | Value |
| --- | --- |
| **Measured size** | ~14.1 MB (`14790453` bytes) for PyInstaller 6.14.2 onefile build on Windows 11 / Python 3.12.10 (2026-08-08) |
| **SmartScreen / AV** | Unsigned PyInstaller onefile builds commonly show Windows SmartScreen (“Windows protected your PC”). Use **More info → Run anyway** when you trust the build source. Clean-folder launch smoke (`%TEMP%\UzbekTTS-clean-smoke\UzbekTTS.exe`) started successfully with no Defender quarantine during local test; still expect SmartScreen on other machines. |
| **Code signing** | Not in MVP scope; consider signing for public releases later. |

## Releasing

1. Tag the release commit.
2. Build `UzbekTTS.exe` on a clean-ish Windows machine with the pinned PyInstaller version.
3. Upload `dist/UzbekTTS.exe` to the GitHub Release (do not commit the binary to git).
4. Paste measured size + any AV notes into the Release body and update the table above.
5. Ensure README screenshots / `assets/demo.gif` match the shipped GUI.
