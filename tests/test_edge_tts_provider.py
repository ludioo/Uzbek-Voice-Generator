import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.providers.edge_tts_provider import EdgeTTSProviderError, synthesize_to_file


class TestSynthesizeToFile(unittest.TestCase):
    def test_happy_path_calls_communicate_and_save(self) -> None:
        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()
        output_path = Path("output/hello.mp3")

        with patch(
            "src.providers.edge_tts_provider.edge_tts.Communicate",
            return_value=mock_communicate,
        ) as mock_cls:
            asyncio.run(
                synthesize_to_file(
                    "Assalomu alaykum",
                    "uz-UZ-MadinaNeural",
                    output_path,
                )
            )

        mock_cls.assert_called_once_with("Assalomu alaykum", "uz-UZ-MadinaNeural")
        mock_communicate.save.assert_awaited_once_with(str(output_path))

    def test_failure_propagates_as_provider_error(self) -> None:
        mock_communicate = MagicMock()
        cause = RuntimeError("no audio")
        mock_communicate.save = AsyncMock(side_effect=cause)

        with patch(
            "src.providers.edge_tts_provider.edge_tts.Communicate",
            return_value=mock_communicate,
        ):
            with self.assertRaises(EdgeTTSProviderError) as ctx:
                asyncio.run(
                    synthesize_to_file(
                        "Assalomu alaykum",
                        "uz-UZ-MadinaNeural",
                        Path("output/hello.mp3"),
                    )
                )

        self.assertIs(ctx.exception.__cause__, cause)


if __name__ == "__main__":
    unittest.main()
