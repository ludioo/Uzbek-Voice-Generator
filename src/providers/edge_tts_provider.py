import logging
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)


class EdgeTTSProviderError(Exception):
    """Raised when Edge TTS synthesis fails."""


async def synthesize_to_file(text: str, voice_id: str, output_path: Path) -> None:
    logger.info(
        "Starting Edge TTS synthesis voice_id=%s path=%s",
        voice_id,
        output_path,
    )
    try:
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(str(output_path))
    except Exception as exc:
        logger.error("Edge TTS synthesis failed: %s", exc)
        raise EdgeTTSProviderError(f"Edge TTS synthesis failed: {exc}") from exc
    logger.info("Edge TTS synthesis succeeded path=%s", output_path)
