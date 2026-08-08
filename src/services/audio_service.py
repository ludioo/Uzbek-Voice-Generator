import logging
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

from src.config.voices import VoicesConfigError, load_voices
from src.models.generation import GenerationRequest, GenerationResult
from src.models.voice import Voice
from src.providers.edge_tts_provider import EdgeTTSProviderError, synthesize_to_file

logger = logging.getLogger(__name__)

SynthesizeFn = Callable[[str, str, Path], Awaitable[None]]

_WINDOWS_FORBIDDEN = set('<>:"|?*')


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _output_dir() -> Path:
    return _project_root() / "output"


def get_output_dir() -> Path:
    return _output_dir()


def _failure(kind: str, message: str) -> GenerationResult:
    return GenerationResult(
        success=False,
        error_message=message,
        error_kind=kind,
    )


def _validate_filename(filename: str) -> str | None:
    name = filename.strip()
    if not name:
        return None
    if ".." in name or "/" in name or "\\" in name:
        return None
    if Path(name).name != name:
        return None
    if any(ch in _WINDOWS_FORBIDDEN for ch in name):
        return None
    if any(ord(ch) < 32 for ch in name):
        return None
    return name


def _validate_output_subdir(subdir: str) -> str | None:
    return _validate_filename(subdir)


def _ensure_mp3_extension(name: str) -> str | None:
    path = Path(name)
    suffix = path.suffix
    if not suffix:
        stem = name
    else:
        stem = path.stem
    if not stem:
        return None
    return f"{stem}.mp3"


def _resolve_output_path(
    filename: str,
    output_subdir: str | None = None,
) -> Path | None:
    output_dir = _output_dir().resolve()
    if output_subdir is None:
        target_dir = output_dir
    else:
        target_dir = (output_dir / output_subdir).resolve()
        try:
            target_dir.relative_to(output_dir)
        except ValueError:
            return None
    candidate = (target_dir / filename).resolve()
    try:
        candidate.relative_to(output_dir)
    except ValueError:
        return None
    return candidate


def _resolve_voice(voices: list[Voice], gender: str) -> Voice | None:
    for voice in voices:
        if voice.gender == gender:
            return voice
    return None


def _has_permission_error(exc: BaseException) -> bool:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, PermissionError):
            return True
        current = current.__cause__
    return False


def _has_network_error(exc: BaseException) -> bool:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, (ConnectionError, TimeoutError)):
            return True
        type_name = type(current).__name__
        if type_name.endswith("ConnectorError") or type_name == "ClientConnectionError":
            return True
        current = current.__cause__
    return False


async def generate_audio(
    request: GenerationRequest,
    *,
    voices_path: Path | None = None,
    synthesize: SynthesizeFn | None = None,
    output_subdir: str | None = None,
) -> GenerationResult:
    synthesize_fn = synthesize if synthesize is not None else synthesize_to_file

    logger.info(
        "Starting audio generation gender=%s filename=%s output_subdir=%s",
        request.gender,
        request.filename,
        output_subdir,
    )

    if not request.text.strip():
        logger.warning("Audio generation failed: empty text")
        return _failure("empty_text", "Text must not be empty")

    safe_subdir: str | None = None
    if output_subdir is not None:
        safe_subdir = _validate_output_subdir(output_subdir)
        if safe_subdir is None:
            logger.warning("Audio generation failed: invalid output subdir")
            return _failure("invalid_filename", "Output folder name is invalid")

    safe_name = _validate_filename(request.filename)
    if safe_name is None:
        logger.warning("Audio generation failed: invalid filename")
        return _failure("invalid_filename", "Filename is invalid")

    safe_name = _ensure_mp3_extension(safe_name)
    if safe_name is None:
        logger.warning("Audio generation failed: invalid filename")
        return _failure("invalid_filename", "Filename is invalid")

    output_path = _resolve_output_path(safe_name, safe_subdir)
    if output_path is None:
        logger.warning("Audio generation failed: path traversal")
        return _failure("invalid_filename", "Filename is invalid")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.error("Audio generation failed: cannot create output folder: %s", exc)
        return _failure("save_permission", "Unable to save the audio file")

    try:
        voices = load_voices(voices_path)
    except VoicesConfigError as exc:
        logger.error("Audio generation failed: config error: %s", exc)
        return _failure("config_error", str(exc))

    voice = _resolve_voice(voices, request.gender)
    if voice is None:
        logger.warning(
            "Audio generation failed: voice not found for gender=%s",
            request.gender,
        )
        return _failure(
            "voice_not_found",
            f"No voice configured for gender '{request.gender}'",
        )

    try:
        await synthesize_fn(request.text, voice.id, output_path)
    except EdgeTTSProviderError as exc:
        logger.error("Audio generation failed: %s", exc)
        if _has_permission_error(exc):
            return _failure("save_permission", "Unable to save the audio file")
        if _has_network_error(exc):
            return _failure(
                "network_unavailable",
                "Network unavailable",
            )
        return _failure("tts_failure", str(exc))
    except Exception as exc:
        logger.error("Unexpected synthesis failure: %s", exc)
        return _failure("tts_failure", str(exc))

    logger.info("Audio generation succeeded path=%s", output_path)
    return GenerationResult(success=True, output_path=str(output_path))
