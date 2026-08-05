import asyncio
import logging
from pathlib import Path

from src.models.generation import GenerationRequest, GenerationResult
from src.services.audio_service import generate_audio
from src.ui.batch_csv import run_batch_csv

logger = logging.getLogger(__name__)

_ERROR_MESSAGES = {
    "empty_text": "Text must not be empty.",
    "invalid_filename": (
        "Filename is invalid. Use a simple name like hello.mp3 (no folders)."
    ),
    "voice_not_found": "Selected voice is not available in config.",
    "config_error": "Voice configuration could not be loaded.",
    "save_permission": "Unable to save the audio file. Check folder permissions.",
    "network_unavailable": (
        "Network unavailable. Check your connection and try again."
    ),
    "tts_failure": (
        "Speech generation failed. Check your network connection and try again."
    ),
}


def _prompt_text() -> str:
    return input("Enter Uzbek text: ")


def _prompt_gender() -> str:
    while True:
        raw = input("Select voice (1=Male, 2=Female): ").strip().lower()
        if raw in {"1", "male", "m"}:
            return "Male"
        if raw in {"2", "female", "f"}:
            return "Female"
        print("Please enter 1/Male or 2/Female.")


def _prompt_filename() -> str:
    return input("Output filename: ")


def _message_for(result: GenerationResult) -> str:
    if result.error_kind and result.error_kind in _ERROR_MESSAGES:
        return _ERROR_MESSAGES[result.error_kind]
    if result.error_message:
        return result.error_message
    return "Generation failed."


async def _run_interactive() -> None:
    text = _prompt_text()
    gender = _prompt_gender()
    filename = _prompt_filename()

    request = GenerationRequest(text=text, gender=gender, filename=filename)
    print("Generating...")
    try:
        result = await generate_audio(request)
    except Exception:
        logger.exception("Unexpected error during audio generation")
        print("An unexpected error occurred. See logs for details.")
        return

    if result.success:
        print(f"Saved: {result.output_path}")
    else:
        print(_message_for(result))


async def run_cli(csv_path: Path | None = None) -> int:
    if csv_path is not None:
        batch_result = await run_batch_csv(csv_path, message_for=_message_for)
        return 1 if batch_result.aborted else 0

    await _run_interactive()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_cli()))
