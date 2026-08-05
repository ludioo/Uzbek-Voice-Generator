import asyncio
import csv
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from src.models.generation import GenerationRequest, GenerationResult
from src.services.audio_service import _validate_output_subdir, generate_audio

logger = logging.getLogger(__name__)

_REQUIRED_COLUMNS = ("text", "gender", "filename")
_ROW_DELAY_SECONDS = 1.0

GenerateFn = Callable[..., Awaitable[GenerationResult]]
SleepFn = Callable[[float], Awaitable[None]]
MessageFn = Callable[[GenerationResult], str]


@dataclass
class BatchCsvResult:
    ok: int = 0
    failed: int = 0
    skipped: int = 0
    aborted: bool = False


def _map_csv_gender(raw: str) -> str | None:
    value = raw.strip()
    if value == "1":
        return "Male"
    if value == "2":
        return "Female"
    return None


def _field(row: dict[str, str | None], key: str) -> str:
    value = row.get(key)
    if value is None:
        return ""
    return value.strip()


def _is_blank_row(text: str, gender: str, filename: str) -> bool:
    return not text and not gender and not filename


async def run_batch_csv(
    csv_path: Path,
    *,
    message_for: MessageFn,
    generate: GenerateFn | None = None,
    sleep: SleepFn | None = None,
) -> BatchCsvResult:
    generate_fn = generate if generate is not None else generate_audio
    sleep_fn = sleep if sleep is not None else asyncio.sleep
    result = BatchCsvResult()

    stem = csv_path.stem
    safe_stem = _validate_output_subdir(stem)
    if safe_stem is None:
        print(
            "CSV file name is invalid for an output folder. "
            "Use a simple basename without folders or special characters."
        )
        result.aborted = True
        return result

    try:
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                print("CSV header is missing. Required columns: text,gender,filename")
                result.aborted = True
                return result

            headers = set(reader.fieldnames)
            missing = [name for name in _REQUIRED_COLUMNS if name not in headers]
            if missing:
                print(
                    "CSV header is invalid. Required columns: text,gender,filename "
                    f"(missing: {', '.join(missing)})"
                )
                result.aborted = True
                return result

            for index, row in enumerate(reader, start=2):
                text = _field(row, "text")
                gender_raw = _field(row, "gender")
                filename = _field(row, "filename")

                if _is_blank_row(text, gender_raw, filename):
                    result.skipped += 1
                    continue

                gender = _map_csv_gender(gender_raw)
                if gender is None:
                    print(f"FAIL row {index}: Gender must be 1 (Male) or 2 (Female).")
                    result.failed += 1
                    await sleep_fn(_ROW_DELAY_SECONDS)
                    continue

                if not filename:
                    print(f"FAIL row {index}: Filename is required.")
                    result.failed += 1
                    await sleep_fn(_ROW_DELAY_SECONDS)
                    continue

                request = GenerationRequest(
                    text=text,
                    gender=gender,
                    filename=filename,
                )
                try:
                    generation = await generate_fn(
                        request,
                        output_subdir=safe_stem,
                    )
                except Exception:
                    logger.exception("Unexpected error during batch row %s", index)
                    print(f"FAIL row {index}: An unexpected error occurred.")
                    result.failed += 1
                    await sleep_fn(_ROW_DELAY_SECONDS)
                    continue

                if generation.success:
                    print(f"OK row {index}: {generation.output_path}")
                    result.ok += 1
                else:
                    print(f"FAIL row {index}: {message_for(generation)}")
                    result.failed += 1

                await sleep_fn(_ROW_DELAY_SECONDS)
    except OSError as exc:
        print(f"Unable to read CSV file: {exc}")
        result.aborted = True
        return result

    print(f"OK={result.ok} FAIL={result.failed} SKIPPED={result.skipped}")
    return result
