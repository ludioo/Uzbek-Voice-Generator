# Uzbek Voice Generator

Windows desktop app that turns Uzbek text into MP3 speech with Microsoft Edge TTS (`edge-tts`). Male and Female voices come from `config/voices.json`.

Internet connection required (Edge TTS is online).

![Demo](assets/demo.gif)

## Quick start (GUI `.exe`)

For non-technical users:

1. Download **`UzbekTTS.exe`** from the [GitHub Releases](https://github.com/ludioo/Uzbek-Voice-Generator/releases) page.
2. Put it in any folder and double-click.
3. Enter Uzbek text (or use **Batch CSV**), choose Male/Female, Generate.
4. MP3s are written next to the exe under `output/`.

If Windows SmartScreen appears (“Windows protected your PC”), choose **More info → Run anyway** when you trust the release. Unsigned PyInstaller builds commonly trigger this.

Typical download size: about **14 MB**.

### Screenshots

| Single text | Batch CSV |
| --- | --- |
| ![Single text](assets/screenshots/single_text.png) | ![Batch progress](assets/screenshots/batch_progress.png) |

Also: ![After generate](assets/screenshots/single_success.png)

### Run GUI from source

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python gui_main.py
```

Or: `python main.py --gui`

## Requirements

- Windows
- Python 3.12 (for source / CLI / building the exe)

## Install (developers)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Dev/build tools (pytest, PyInstaller):

```powershell
pip install -r requirements-dev.txt
```

## Tests

```powershell
pytest
```

Unit tests only; no live Edge TTS network calls are required.

## CLI

### Interactive (one file)

```powershell
python main.py
```

Enter Uzbek text, choose Male or Female, and set an output filename. The MP3 is written under `output/`. A bare basename like `hello` is enough — `.mp3` is added or normalized automatically.

### Batch from CSV

```powershell
python main.py --csv examples/sample_batch.csv
```

UTF-8 CSV must include columns `text`, `gender`, `filename` (exact names). Extra columns are ignored. Files saved from Excel as “CSV UTF-8” (with BOM) are supported.

Batch output goes under `output/<csv_stem>/` (from the CSV basename). Example: `examples/uzbek_tts_manifest.csv` → `output/uzbek_tts_manifest/*.mp3`. Interactive mode and GUI single-text still write directly under `output/`.

- `gender`: `1` = Male, `2` = Female only
- `filename`: required on every non-empty row (`.mp3` is normalized by the service)
- Quote `text` values that contain commas (standard CSV quoting)
- Failed rows are reported and skipped; the batch continues
- Existing files in the batch output folder are overwritten
- There is a 1 second delay after each non-skipped row
- Console shows per-row OK/FAIL and a final `OK=… FAIL=… SKIPPED=…` summary

See [`examples/sample_batch.csv`](examples/sample_batch.csv).

## Build the Windows `.exe`

```powershell
pip install -r requirements-dev.txt
pyinstaller uzbek_tts_gui.spec
```

Artifact: `dist/UzbekTTS.exe` (onefile, no console). When frozen, `config/voices.json` is bundled and `output/` is created beside the exe.

## Troubleshooting

- Empty text or invalid filename → clear message; use a simple basename like `hello` or `hello.mp3` (no folders or `..`). Wrong extensions (e.g. `.wav`) are normalized to `.mp3`.
- Batch CSV missing columns or unreadable file → process exits / aborts before generating audio.
- Network / TTS failure → check your internet connection and try again.
- Save permission failure → ensure the `output/` folder is writable.
- GUI logs appear at INFO and above when run from source; packaged exe surfaces failures via dialogs.

## Layout

- `gui_main.py` — GUI entry
- `main.py` — CLI (and `--gui`)
- `src/config/` — voice config loading
- `src/models/` — pure data models
- `src/providers/` — Edge TTS integration
- `src/services/` — generation orchestration
- `src/ui/` — CLI + CustomTkinter GUI
- `config/voices.json` — voice definitions
- `examples/` — sample batch CSV
- `assets/` — screenshots and demo GIF
- `output/` — generated MP3 files
- `uzbek_tts_gui.spec` — PyInstaller recipe
