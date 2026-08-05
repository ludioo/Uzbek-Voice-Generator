import unittest

from src.models import GenerationRequest, GenerationResult, Voice


class TestVoice(unittest.TestCase):
    def test_sardor_round_trip(self) -> None:
        voice = Voice(
            id="uz-UZ-SardorNeural",
            name="Sardor",
            gender="Male",
            language="Uzbek",
        )
        self.assertEqual(voice.id, "uz-UZ-SardorNeural")
        self.assertEqual(voice.name, "Sardor")
        self.assertEqual(voice.gender, "Male")
        self.assertEqual(voice.language, "Uzbek")

    def test_madina_round_trip(self) -> None:
        voice = Voice(
            id="uz-UZ-MadinaNeural",
            name="Madina",
            gender="Female",
            language="Uzbek",
        )
        self.assertEqual(voice.id, "uz-UZ-MadinaNeural")
        self.assertEqual(voice.name, "Madina")
        self.assertEqual(voice.gender, "Female")
        self.assertEqual(voice.language, "Uzbek")


class TestGenerationRequest(unittest.TestCase):
    def test_request_fields(self) -> None:
        request = GenerationRequest(
            text="Assalomu alaykum",
            gender="Female",
            filename="hello.mp3",
        )
        self.assertEqual(request.text, "Assalomu alaykum")
        self.assertEqual(request.gender, "Female")
        self.assertEqual(request.filename, "hello.mp3")


class TestGenerationResult(unittest.TestCase):
    def test_success_result(self) -> None:
        result = GenerationResult(
            success=True,
            output_path="output/hello.mp3",
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output_path, "output/hello.mp3")
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.error_kind)

    def test_failure_result(self) -> None:
        result = GenerationResult(
            success=False,
            error_message="Text must not be empty",
            error_kind="empty_text",
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertEqual(result.error_message, "Text must not be empty")
        self.assertEqual(result.error_kind, "empty_text")


if __name__ == "__main__":
    unittest.main()
