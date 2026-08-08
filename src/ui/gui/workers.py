# Background workers for off-main-thread TTS/batch (milestones G4–G6).

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Callable
from pathlib import Path

from src.models.generation import GenerationRequest, GenerationResult
from src.services.audio_service import generate_audio
from src.ui.batch_csv import BatchCsvResult, BatchProgressEvent, run_batch_csv
from src.ui.messages import message_for

logger = logging.getLogger(__name__)

UNEXPECTED_ERROR = "unexpected_error"

DoneCallback = Callable[[GenerationResult | str], None]
BatchProgressCallback = Callable[[BatchProgressEvent], None]
BatchDoneCallback = Callable[[BatchCsvResult | str], None]


class GenerateWorker(threading.Thread):
    def __init__(
        self,
        request: GenerationRequest,
        on_done: DoneCallback,
    ) -> None:
        super().__init__(daemon=True)
        self._request = request
        self._on_done = on_done

    def run(self) -> None:
        try:
            result = asyncio.run(generate_audio(self._request))
        except Exception:
            logger.exception("Unexpected error during audio generation")
            self._on_done(UNEXPECTED_ERROR)
            return
        self._on_done(result)


class BatchWorker(threading.Thread):
    def __init__(
        self,
        csv_path: Path,
        on_progress: BatchProgressCallback,
        on_done: BatchDoneCallback,
    ) -> None:
        super().__init__(daemon=True)
        self._csv_path = csv_path
        self._on_progress = on_progress
        self._on_done = on_done

    def run(self) -> None:
        try:
            result = asyncio.run(
                run_batch_csv(
                    self._csv_path,
                    message_for=message_for,
                    report=self._on_progress,
                )
            )
        except Exception:
            logger.exception("Unexpected error during batch CSV")
            self._on_done(UNEXPECTED_ERROR)
            return
        self._on_done(result)
