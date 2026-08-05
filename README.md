# Uzbek Voice Generator

CLI MVP that converts Uzbek text to MP3 speech using Microsoft Edge TTS (`edge-tts`). Male and Female voices are loaded from `config/voices.json`.

## Requirements

- Windows
- Python 3.12

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Tests

```powershell
pip install -r requirements-dev.txt
pytest
```

Unit tests only; no live Edge TTS network calls are required.

## Run

### Interactive (one file)

```powershell
python main.py
```

This starts the interactive CLI: enter Uzbek text, choose Male or Female, and set an output filename. The MP3 is written under `output/`. A bare basename like `hello` is enough — `.mp3` is added or normalized automatically.

### Batch from CSV

```powershell
python main.py --csv examples/sample_batch.csv
```

UTF-8 CSV must include columns `text`, `gender`, `filename` (exact names). Extra columns are ignored. Files saved from Excel as “CSV UTF-8” (with BOM) are supported.

Batch output goes under `output/<csv_stem>/` (from the CSV basename). Example: `examples/uzbek_tts_manifest.csv` → `output/uzbek_tts_manifest/*.mp3`. Interactive mode still writes directly under `output/`.

- `gender`: `1` = Male, `2` = Female only
- `filename`: required on every non-empty row (`.mp3` is normalized by the service)
- Quote `text` values that contain commas (standard CSV quoting)
- Failed rows are reported and skipped; the batch continues
- Existing files in the batch output folder are overwritten
- There is a 1 second delay after each non-skipped row
- Console shows per-row OK/FAIL and a final `OK=… FAIL=… SKIPPED=…` summary

See [`examples/sample_batch.csv`](examples/sample_batch.csv).

## Troubleshooting

- Empty text or invalid filename → the CLI shows a clear message; use a simple basename like `hello` or `hello.mp3` (no folders or `..`). Wrong extensions (e.g. `.wav`) are normalized to `.mp3`.
- Batch CSV missing columns or unreadable file → process exits with code 1 before generating audio.
- Network / TTS failure → check your internet connection and try again.
- Save permission failure → ensure the `output/` folder is writable.
- Logs appear in the console at INFO and above (warnings and errors included).

## Layout

- `src/config/` — voice config loading
- `src/models/` — pure data models
- `src/providers/` — Edge TTS integration
- `src/services/` — generation orchestration
- `src/ui/` — CLI presentation (interactive + CSV batch)
- `config/voices.json` — voice definitions
- `examples/` — sample batch CSV
- `output/` — generated MP3 files
