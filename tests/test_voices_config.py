import json
import tempfile
import unittest
from pathlib import Path

from src.config import VoicesConfigError, load_voices


class TestLoadVoices(unittest.TestCase):
    def test_load_real_voices_json(self) -> None:
        voices = load_voices()
        self.assertEqual(len(voices), 2)
        genders = {voice.gender for voice in voices}
        self.assertEqual(genders, {"Male", "Female"})
        ids = {voice.id for voice in voices}
        self.assertEqual(
            ids,
            {"uz-UZ-SardorNeural", "uz-UZ-MadinaNeural"},
        )

    def test_load_temp_fixture(self) -> None:
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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voices.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            voices = load_voices(path)

        self.assertEqual(len(voices), 2)
        self.assertEqual(voices[0].gender, "Male")
        self.assertEqual(voices[0].name, "Sardor")
        self.assertEqual(voices[1].gender, "Female")
        self.assertEqual(voices[1].name, "Madina")

    def test_missing_file(self) -> None:
        missing = Path("nonexistent") / "voices.json"
        with self.assertRaises(VoicesConfigError):
            load_voices(missing)

    def test_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voices.json"
            path.write_text("{not-valid-json", encoding="utf-8")
            with self.assertRaises(VoicesConfigError):
                load_voices(path)

    def test_empty_voices_array(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voices.json"
            path.write_text(json.dumps({"voices": []}), encoding="utf-8")
            with self.assertRaises(VoicesConfigError):
                load_voices(path)

    def test_missing_required_field(self) -> None:
        payload = {
            "voices": [
                {
                    "name": "Sardor",
                    "gender": "Male",
                    "language": "Uzbek",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voices.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(VoicesConfigError):
                load_voices(path)


if __name__ == "__main__":
    unittest.main()
