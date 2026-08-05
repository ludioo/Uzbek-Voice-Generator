import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.models.generation import GenerationRequest, GenerationResult
from src.ui.batch_csv import run_batch_csv


def _message_for(result: GenerationResult) -> str:
    if result.error_message:
        return result.error_message
    return "Generation failed."


class TestBatchCsv(unittest.TestCase):
    def test_two_valid_rows(self) -> None:
        generate = AsyncMock(
            side_effect=[
                GenerationResult(success=True, output_path="output/a.mp3"),
                GenerationResult(success=True, output_path="output/b.mp3"),
            ]
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "text,gender,filename\n"
                "Salom,1,a.mp3\n"
                "Assalom,2,b.mp3\n",
                encoding="utf-8",
            )
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertFalse(result.aborted)
        self.assertEqual(result.ok, 2)
        self.assertEqual(result.failed, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(generate.await_count, 2)
        first = generate.await_args_list[0].args[0]
        second = generate.await_args_list[1].args[0]
        self.assertIsInstance(first, GenerationRequest)
        self.assertEqual(first.gender, "Male")
        self.assertEqual(first.filename, "a.mp3")
        self.assertEqual(second.gender, "Female")
        self.assertEqual(second.filename, "b.mp3")
        self.assertEqual(
            generate.await_args_list[0].kwargs.get("output_subdir"),
            "batch",
        )
        self.assertEqual(
            generate.await_args_list[1].kwargs.get("output_subdir"),
            "batch",
        )
        self.assertEqual(sleep.await_count, 2)
        sleep.assert_awaited_with(1.0)

    def test_passes_csv_stem_as_output_subdir(self) -> None:
        generate = AsyncMock(
            return_value=GenerationResult(
                success=True,
                output_path="output/uzbek_tts_manifest/a.mp3",
            )
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "uzbek_tts_manifest.csv"
            csv_path.write_text(
                "text,gender,filename\nSalom,1,a.mp3\n",
                encoding="utf-8",
            )
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertFalse(result.aborted)
        self.assertEqual(result.ok, 1)
        generate.assert_awaited_once()
        self.assertEqual(
            generate.await_args.kwargs.get("output_subdir"),
            "uzbek_tts_manifest",
        )

    def test_unsafe_csv_stem_aborts(self) -> None:
        generate = AsyncMock()
        sleep = AsyncMock()
        csv_path = Path("bad:name.csv")
        result = asyncio.run(
            run_batch_csv(
                csv_path,
                message_for=_message_for,
                generate=generate,
                sleep=sleep,
            )
        )

        self.assertTrue(result.aborted)
        generate.assert_not_awaited()
        sleep.assert_not_awaited()

    def test_invalid_gender_continues(self) -> None:
        generate = AsyncMock(
            return_value=GenerationResult(success=True, output_path="output/ok.mp3")
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "text,gender,filename\n"
                "Bad,3,bad.mp3\n"
                "Good,1,ok.mp3\n",
                encoding="utf-8",
            )
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertEqual(result.ok, 1)
        self.assertEqual(result.failed, 1)
        self.assertEqual(generate.await_count, 1)
        self.assertEqual(generate.await_args.args[0].gender, "Male")
        self.assertEqual(sleep.await_count, 2)

    def test_missing_header_aborts(self) -> None:
        generate = AsyncMock()
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text("text,filename\nSalom,a.mp3\n", encoding="utf-8")
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertTrue(result.aborted)
        generate.assert_not_awaited()
        sleep.assert_not_awaited()

    def test_extra_columns_ignored(self) -> None:
        generate = AsyncMock(
            return_value=GenerationResult(success=True, output_path="output/a.mp3")
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "id,text,gender,filename,notes\n"
                "1,Salom,1,a.mp3,ignore-me\n",
                encoding="utf-8",
            )
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertEqual(result.ok, 1)
        request = generate.await_args.args[0]
        self.assertEqual(request.text, "Salom")
        self.assertEqual(request.filename, "a.mp3")

    def test_blank_row_skipped(self) -> None:
        generate = AsyncMock(
            return_value=GenerationResult(success=True, output_path="output/a.mp3")
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "text,gender,filename\n"
                ",,\n"
                "Salom,1,a.mp3\n",
                encoding="utf-8",
            )
            result = asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.ok, 1)
        self.assertEqual(generate.await_count, 1)
        self.assertEqual(sleep.await_count, 1)

    def test_service_failure_continues(self) -> None:
        generate = AsyncMock(
            side_effect=[
                GenerationResult(
                    success=False,
                    error_kind="tts_failure",
                    error_message="boom",
                ),
                GenerationResult(success=True, output_path="output/b.mp3"),
            ]
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "text,gender,filename\n"
                "Fail,1,a.mp3\n"
                "Ok,2,b.mp3\n",
                encoding="utf-8",
            )
            with patch("builtins.print") as mock_print:
                result = asyncio.run(
                    run_batch_csv(
                        csv_path,
                        message_for=_message_for,
                        generate=generate,
                        sleep=sleep,
                    )
                )

        self.assertEqual(result.ok, 1)
        self.assertEqual(result.failed, 1)
        self.assertEqual(generate.await_count, 2)
        self.assertEqual(sleep.await_count, 2)
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("FAIL row 2", printed)
        self.assertIn("OK row 3", printed)

    def test_filename_passed_through(self) -> None:
        generate = AsyncMock(
            return_value=GenerationResult(success=True, output_path="output/CO_Uzb_4.mp3")
        )
        sleep = AsyncMock()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "batch.csv"
            csv_path.write_text(
                "text,gender,filename\nSalom,1,CO_Uzb_4\n",
                encoding="utf-8",
            )
            asyncio.run(
                run_batch_csv(
                    csv_path,
                    message_for=_message_for,
                    generate=generate,
                    sleep=sleep,
                )
            )

        self.assertEqual(generate.await_args.args[0].filename, "CO_Uzb_4")


if __name__ == "__main__":
    unittest.main()
