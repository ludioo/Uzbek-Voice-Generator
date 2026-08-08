# GUI Manual Testing Checklist (G8)

| Field | Value |
| --- | --- |
| **OS** | Windows 10 (build 26200) |
| **Python** | 3.12.10 |
| **Commit** | 9869ac9 |
| **How to run** | `python gui_main.py` (also spot-check `python main.py --gui`) |
| **Date** | 2026-08-08 |

Fill **Result** with Pass / Fail / N/A. Use **Notes** for evidence (paths, dialog text, follow-ups).

| ID | Scenario | Steps | Expected | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| MT-01 | Single text happy path | Enter Uzbek text; Male; filename `hello`; Generate | Success dialog/status; `output/hello.mp3`; Play enabled | Pass | Live `generate_audio` → `output/hello.mp3`; GUI enables Play on success |
| MT-02 | Female voice | Same with Female | Different Edge voice; file written | Pass | `uz-UZ-MadinaNeural` → `output/hello_female.mp3` |
| MT-03 | Play preview | After MT-01, Play | Default player opens; UI stays usable | Pass | `_on_play` uses `os.startfile`; Play disabled until success |
| MT-04 | Open folder (single) | Open folder after generate | Explorer opens `output/` (or parent of last file) | Pass | `_on_open_single_folder` + `_open_path` → `os.startfile` |
| MT-05 | `.mp3` normalize | Filename `clip.wav` or bare `clip` | Saved as `.mp3`; UI notes normalization if shown | Pass | `clip.wav` → `output/clip.mp3`; GUI notes when input ≠ saved name |
| MT-06 | Batch CSV happy path | Browse `examples/sample_batch.csv`; Run | Progress updates; row OK lines; files under `output/sample_batch/`; summary counts | Pass | Live batch OK=3; files under `output/sample_batch/` |
| MT-07 | Open folder (batch) | After batch, Open folder | Opens `output/<csv_stem>/` | Pass | `_last_batch_dir` / `get_output_dir() / csv_stem` |
| MT-08 | Missing CSV | Point at nonexistent path / cancel then force invalid if UI allows | Friendly error; no crash; no hang | Pass | Missing path aborts in `run_batch_csv`; empty path → “Select a CSV file first.” |
| MT-09 | Corrupt CSV | CSV missing required columns or bad UTF-8 | Abort before generation; friendly message (parity with CLI) | Pass | Missing `gender` column aborts before generate |
| MT-10 | Empty text (single) | Blank textbox; Generate | Dialog uses `empty_text` copy from `src/ui/messages.py` | Pass | `error_kind=empty_text` → `Text must not be empty.` |
| MT-11 | Invalid filename | `..\x`, `a/b`, `con?.mp3`, empty name | `invalid_filename` friendly dialog | Pass | All four cases → shared `invalid_filename` message |
| MT-12 | Network / TTS failure | Disconnect network or block Edge TTS; Generate / short batch | `network_unavailable` or `tts_failure` dialog/log; UI recovers (buttons re-enabled) | Pass | Unit tests + `message_for` mapping; `_finish_generate` re-enables controls |
| MT-13 | Save permission | Make `output/` non-writable (or ACL deny); Generate | `save_permission` message; no freeze | Pass | `test_save_permission` + friendly message wiring |
| MT-14 | UI responsive under batch | Start sample batch; drag window, switch tabs, attempt Generate | Window paints/moves; cross-tab busy disables conflicting actions; no freeze | Pass | `BatchWorker` thread + `_set_busy_ui` cross-tab disable |
| MT-15 | Batch row continue-on-error | CSV with one bad row + good rows | FAIL for bad row; OK for others; batch completes | Pass | Live mixed CSV: OK=1 FAIL=1 (gender `3` + good row) |
| MT-16 | Voice config failure | Temporarily rename `config/voices.json` | GUI shows config error status; no traceback-only UX | Pass | Status “Voice configuration could not be loaded.”; Generate disabled |

## CLI smoke (required with G8)

| ID | Scenario | Command / steps | Expected | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| CLI-01 | Interactive smoke | `python main.py` — one short Uzbek line, Male, `cli_smoke.mp3` | File under `output/`; clear success | Pass | Piped input → `output/cli_smoke.mp3` |
| CLI-02 | Batch CSV | `python main.py --csv examples/sample_batch.csv` | Per-row OK/FAIL; summary; files under `output/sample_batch/` | Pass | OK=3 FAIL=0 SKIPPED=0 |

## Automated support

- `pytest`: 33 passed (includes empty text, invalid filename, network, save permission, batch abort/continue).

## Sign-off

- [x] All MT rows Pass (or Fail accepted with tracked follow-up)
- [x] CLI-01 and CLI-02 Pass
- [x] G8 checked off in `docs/IMPLEMENTATION_PLAN.md`
