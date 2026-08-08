import json
import sys
from pathlib import Path

from src.models.voice import Voice

_REQUIRED_FIELDS = ("id", "name", "gender", "language")


class VoicesConfigError(Exception):
    """Raised when voices configuration cannot be loaded or validated."""


def _default_voices_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "config" / "voices.json"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2] / "config" / "voices.json"


def _parse_voice(entry: object, index: int) -> Voice:
    if not isinstance(entry, dict):
        raise VoicesConfigError(
            f"Voice entry at index {index} must be an object, got {type(entry).__name__}"
        )

    values: dict[str, str] = {}
    for field in _REQUIRED_FIELDS:
        if field not in entry:
            raise VoicesConfigError(
                f"Voice entry at index {index} is missing required field '{field}'"
            )
        raw = entry[field]
        if not isinstance(raw, str) or not raw.strip():
            raise VoicesConfigError(
                f"Voice entry at index {index} field '{field}' must be a non-empty string"
            )
        values[field] = raw.strip()

    return Voice(
        id=values["id"],
        name=values["name"],
        gender=values["gender"],
        language=values["language"],
    )


def load_voices(config_path: Path | None = None) -> list[Voice]:
    path = config_path if config_path is not None else _default_voices_path()

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise VoicesConfigError(f"Voices config file not found: {path}") from exc
    except OSError as exc:
        raise VoicesConfigError(f"Unable to read voices config file: {path}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VoicesConfigError(f"Invalid JSON in voices config file: {path}") from exc

    if not isinstance(data, dict):
        raise VoicesConfigError(
            f"Voices config root must be an object, got {type(data).__name__}: {path}"
        )

    if "voices" not in data:
        raise VoicesConfigError(f"Voices config missing 'voices' key: {path}")

    voices_raw = data["voices"]
    if not isinstance(voices_raw, list):
        raise VoicesConfigError(
            f"'voices' must be a list, got {type(voices_raw).__name__}: {path}"
        )

    if len(voices_raw) == 0:
        raise VoicesConfigError(f"'voices' array must not be empty: {path}")

    return [_parse_voice(entry, index) for index, entry in enumerate(voices_raw)]
