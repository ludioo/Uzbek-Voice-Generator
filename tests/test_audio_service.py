import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from src.models.generation import GenerationRequest
from src.providers.edge_tts_provider import EdgeTTSProviderError
from src.services.audio_service import _output_dir, generate_audio


def _write_voices_fixture(path: Path) -> None:
    payload = {
        "voices": [
            {
                "id": "uz-UZ-SardorNeural",
                "name": "Sardor",
                "gender": "Male",
                "language": "Uzbek",
            },
            {
                "id": "uz-UZ-MadinaNeural",
                "name": "Madina",
                "gender": "Female",
                "language": "Uzbek",
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestGenerateAudio(unittest.TestCase):
    def test_empty_text(self) -> None:
        synthesize = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(text="   ", gender="Female", filename="hello.mp3"),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error_kind, "empty_text")
        synthesize.assert_not_awaited()

    def test_invalid_filenames(self) -> None:
        synthesize = AsyncMock()
        invalid_names = ["", "../secret.mp3", "foo/bar.mp3", "..\\evil.mp3"]
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            for name in invalid_names:
                with self.subTest(filename=name):
                    result = asyncio.run(
                        generate_audio(
                            GenerationRequest(
                                text="Assalomu alaykum",
                                gender="Female",
                                filename=name,
                            ),
                            voices_path=voices_path,
                            synthesize=synthesize,
                        )
                    )
                    self.assertFalse(result.success)
                    self.assertEqual(result.error_kind, "invalid_filename")
        synthesize.assert_not_awaited()

    def test_happy_path_mocked_female(self) -> None:
        synthesize = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Female",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.output_path)
        assert result.output_path is not None
        output_path = Path(result.output_path).resolve()
        self.assertEqual(output_path.name, "hello.mp3")
        self.assertTrue(str(output_path).startswith(str(_output_dir().resolve())))
        synthesize.assert_awaited_once()
        args = synthesize.await_args
        assert args is not None
        self.assertEqual(args.args[0], "Assalomu alaykum")
        self.assertEqual(args.args[1], "uz-UZ-MadinaNeural")
        self.assertEqual(Path(args.args[2]).name, "hello.mp3")
        self.assertEqual(Path(args.args[2]).parent, _output_dir().resolve())

    def test_output_subdir_path(self) -> None:
        synthesize = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Female",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                    output_subdir="uzbek_tts_manifest",
                )
            )

        self.assertTrue(result.success)
        assert result.output_path is not None
        output_path = Path(result.output_path).resolve()
        expected_dir = (_output_dir() / "uzbek_tts_manifest").resolve()
        self.assertEqual(output_path.parent, expected_dir)
        self.assertEqual(output_path.name, "hello.mp3")
        self.assertTrue(expected_dir.is_dir())
        synthesize.assert_awaited_once()
        args = synthesize.await_args
        assert args is not None
        self.assertEqual(Path(args.args[2]).resolve(), output_path)

    def test_invalid_output_subdir(self) -> None:
        synthesize = AsyncMock()
        invalid_subdirs = ["", "..", "a/b", "a\\b", "bad:name"]
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            for subdir in invalid_subdirs:
                with self.subTest(output_subdir=subdir):
                    result = asyncio.run(
                        generate_audio(
                            GenerationRequest(
                                text="Assalomu alaykum",
                                gender="Female",
                                filename="hello.mp3",
                            ),
                            voices_path=voices_path,
                            synthesize=synthesize,
                            output_subdir=subdir,
                        )
                    )
                    self.assertFalse(result.success)
                    self.assertEqual(result.error_kind, "invalid_filename")
        synthesize.assert_not_awaited()

    def test_filename_extension_normalization(self) -> None:
        cases = [
            ("CO_Uzb_4", "CO_Uzb_4.mp3"),
            ("sample.wav", "sample.mp3"),
            ("Hello.MP3", "Hello.mp3"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            for raw_name, expected_name in cases:
                with self.subTest(filename=raw_name):
                    synthesize = AsyncMock()
                    result = asyncio.run(
                        generate_audio(
                            GenerationRequest(
                                text="Assalomu alaykum",
                                gender="Female",
                                filename=raw_name,
                            ),
                            voices_path=voices_path,
                            synthesize=synthesize,
                        )
                    )
                    self.assertTrue(result.success)
                    assert result.output_path is not None
                    self.assertEqual(Path(result.output_path).name, expected_name)
                    synthesize.assert_awaited_once()
                    args = synthesize.await_args
                    assert args is not None
                    self.assertEqual(Path(args.args[2]).name, expected_name)

    def test_unknown_gender(self) -> None:
        synthesize = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Unknown",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error_kind, "voice_not_found")
        synthesize.assert_not_awaited()

    def test_tts_failure(self) -> None:
        synthesize = AsyncMock(side_effect=EdgeTTSProviderError("boom"))
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Female",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error_kind, "tts_failure")

    def test_save_permission(self) -> None:
        err = EdgeTTSProviderError("save failed")
        err.__cause__ = PermissionError("denied")
        synthesize = AsyncMock(side_effect=err)
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Female",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error_kind, "save_permission")

    def test_network_unavailable(self) -> None:
        err = EdgeTTSProviderError("network failed")
        err.__cause__ = ConnectionError("offline")
        synthesize = AsyncMock(side_effect=err)
        with tempfile.TemporaryDirectory() as tmp:
            voices_path = Path(tmp) / "voices.json"
            _write_voices_fixture(voices_path)
            result = asyncio.run(
                generate_audio(
                    GenerationRequest(
                        text="Assalomu alaykum",
                        gender="Female",
                        filename="hello.mp3",
                    ),
                    voices_path=voices_path,
                    synthesize=synthesize,
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error_kind, "network_unavailable")


if __name__ == "__main__":
    unittest.main()
