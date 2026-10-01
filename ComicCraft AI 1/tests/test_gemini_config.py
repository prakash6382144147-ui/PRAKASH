import unittest
from unittest.mock import patch

from app.ai.gemini_flash import generate_outline
from app.config import normalize_gemini_model


class GeminiModelNormalizationTest(unittest.TestCase):
    def test_replaces_deprecated_flash_model(self):
        self.assertEqual(
            normalize_gemini_model("models/gemini-2.5-flash"),
            "gemini-3.8-flash",
        )

    def test_keeps_supported_model_name(self):
        self.assertEqual(
            normalize_gemini_model("gemini-3.8-flash"),
            "gemini-3.8-flash",
        )

    @patch("app.ai.gemini_flash.genai")
    @patch("app.ai.gemini_flash.get_settings")
    def test_falls_back_to_demo_when_gemini_is_unavailable(self, mock_get_settings, mock_genai):
        mock_get_settings.return_value = type(
            "Settings",
            (),
            {
                "gemini_api_key": "abc",
                "comic_panels": 5,
                "gemini_flash_model": "gemini-3.8-flash",
            },
        )()

        class FakeClient:
            class models:
                @staticmethod
                def generate_content(*args, **kwargs):
                    raise Exception("503 UNAVAILABLE. This model is currently experiencing high demand.")

        mock_genai.Client.return_value = FakeClient()

        result = generate_outline(
            "A brave fox explores a forest",
            "Alex",
            "enchanted forest",
            "dramatic",
            "comic book",
        )

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["panel_number"], 1)
        self.assertIn("Alex", result[0]["image_prompt"])


if __name__ == "__main__":
    unittest.main()
